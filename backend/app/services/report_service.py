"""
ReportService — deterministic, SQL-aggregation-based report generation.

Design principles:
- All metrics computed via SQL GROUP BY / CASE / CTEs — no Python iteration over ORM collections.
- UTC datetime used for all comparisons.
- NULL created_by_user_id excluded from both authored categories.
- Cycle time: first TODO→IN_PROGRESS start, first *→COMPLETED end, only completed tasks,
  average returned in hours.
- completion_rate = completed / total, 0.0 when total == 0.
"""

from datetime import date, datetime, timedelta
from typing import List, Optional

from sqlalchemy import and_, func, case, exists, select
from sqlalchemy.orm import Session

from app.models.activity import ProjectActivity
from app.models.project import Project, ProjectStatusEnum
from app.models.task import Task, TaskStatusEnum, WorkUpdate, TaskTransition
from app.models.team import Team, team_projects
from app.models.user import User, Worker, WorkerStatusEnum
from app.schemas.reports import (
    ActivityReport,
    ActivityReportItem,
    OrganizationSummaryReport,
    ProjectPerformanceReport,
    ReportMetadata,
    TeamPerformanceReport,
    WorkerPerformanceReport,
)


def _cycle_time_hours(db: Session, task_filter) -> Optional[float]:
    """
    Compute average cycle time in hours for a set of tasks identified by `task_filter`
    (a SQLAlchemy column expression applied to Task).

    Only COMPLETED tasks with both a TODO→IN_PROGRESS start and a *→COMPLETED
    end transition contribute to the average. Tasks missing either timestamp are excluded.
    """
    started_cte = (
        db.query(
            TaskTransition.task_id,
            func.min(TaskTransition.timestamp).label("started_at"),
        )
        .filter(
            TaskTransition.from_status == TaskStatusEnum.TODO,
            TaskTransition.to_status == TaskStatusEnum.IN_PROGRESS,
        )
        .group_by(TaskTransition.task_id)
        .cte("started_cte")
    )

    completed_cte = (
        db.query(
            TaskTransition.task_id,
            func.min(TaskTransition.timestamp).label("completed_at"),
        )
        .filter(TaskTransition.to_status == TaskStatusEnum.COMPLETED)
        .group_by(TaskTransition.task_id)
        .cte("completed_cte")
    )

    rows = (
        db.query(started_cte.c.started_at, completed_cte.c.completed_at)
        .join(completed_cte, started_cte.c.task_id == completed_cte.c.task_id)
        .join(Task, Task.id == started_cte.c.task_id)
        .filter(Task.status == TaskStatusEnum.COMPLETED, task_filter)
        .all()
    )

    valid = [(s, c) for s, c in rows if c > s]
    if not valid:
        return None
    total_seconds = sum((c - s).total_seconds() for s, c in valid)
    return total_seconds / 3600.0 / len(valid)



class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def _metadata(self, report_type: str) -> ReportMetadata:
        return ReportMetadata(generated_at=datetime.utcnow(), report_type=report_type)

    # ─── Organization ────────────────────────────────────────────────────────

    def get_organization_report(self) -> OrganizationSummaryReport:
        today = date.today()

        worker_stats = self.db.query(
            func.count(Worker.id).label("total"),
            func.sum(case((Worker.status == WorkerStatusEnum.ACTIVE, 1), else_=0)).label("active"),
        ).first()

        total_workers = worker_stats.total or 0
        active_workers = int(worker_stats.active or 0)
        total_teams = self.db.query(func.count(Team.id)).scalar() or 0

        proj_stats = self.db.query(
            func.count(Project.id).label("total"),
            func.sum(case((Project.status == ProjectStatusEnum.ACTIVE, 1), else_=0)).label("active"),
        ).first()
        total_projects = proj_stats.total or 0
        active_projects = int(proj_stats.active or 0)

        task_stats = self.db.query(
            func.count(Task.id).label("total"),
            func.sum(case((Task.status == TaskStatusEnum.COMPLETED, 1), else_=0)).label("completed"),
            func.sum(case((Task.status == TaskStatusEnum.BLOCKED, 1), else_=0)).label("blocked"),
        ).first()
        total_tasks = task_stats.total or 0
        completed_tasks = int(task_stats.completed or 0)
        blocked_tasks = int(task_stats.blocked or 0)
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0.0

        overdue_tasks = (
            self.db.query(func.count(Task.id))
            .filter(Task.status != TaskStatusEnum.COMPLETED, Task.due_date < today)
            .scalar()
            or 0
        )
        unassigned_tasks = (
            self.db.query(func.count(Task.id)).filter(Task.assignee_id.is_(None)).scalar() or 0
        )

        return OrganizationSummaryReport(
            metadata=self._metadata("organization"),
            total_workers=total_workers,
            active_workers=active_workers,
            total_teams=total_teams,
            total_projects=total_projects,
            active_projects=active_projects,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            completion_rate=completion_rate,
            overdue_tasks=overdue_tasks,
            blocked_tasks=blocked_tasks,
            unassigned_tasks=unassigned_tasks,
        )

    # ─── Project ─────────────────────────────────────────────────────────────

    def get_project_report(self, project: Project) -> ProjectPerformanceReport:
        today = date.today()
        pid = project.id

        status_counts = dict(
            self.db.query(Task.status, func.count(Task.id))
            .filter(Task.project_id == pid)
            .group_by(Task.status)
            .all()
        )
        todo = status_counts.get(TaskStatusEnum.TODO, 0)
        in_progress = status_counts.get(TaskStatusEnum.IN_PROGRESS, 0)
        blocked = status_counts.get(TaskStatusEnum.BLOCKED, 0)
        completed = status_counts.get(TaskStatusEnum.COMPLETED, 0)
        total = todo + in_progress + blocked + completed

        overdue = (
            self.db.query(func.count(Task.id))
            .filter(
                Task.project_id == pid,
                Task.status != TaskStatusEnum.COMPLETED,
                Task.due_date < today,
            )
            .scalar()
            or 0
        )
        unassigned = (
            self.db.query(func.count(Task.id))
            .filter(Task.project_id == pid, Task.assignee_id.is_(None))
            .scalar()
            or 0
        )

        completion_rate = completed / total if total > 0 else 0.0
        avg_ct = _cycle_time_hours(self.db, Task.project_id == pid)

        total_upd, worker_auth, mgmt_auth = self._project_activity_counts(pid)

        return ProjectPerformanceReport(
            metadata=self._metadata("project"),
            project_id=project.id,
            project_name=project.name,
            project_status=project.status.value,
            project_health=project.health.value,
            total_tasks=total,
            todo_tasks=todo,
            in_progress_tasks=in_progress,
            blocked_tasks=blocked,
            completed_tasks=completed,
            overdue_tasks=overdue,
            unassigned_tasks=unassigned,
            total_updates=total_upd,
            worker_authored_updates=worker_auth,
            management_authored_updates=mgmt_auth,
            completion_rate=completion_rate,
            average_cycle_time_hours=avg_ct,
        )

    def _project_activity_counts(self, project_id: str) -> tuple[int, int, int]:
        result = (
            self.db.query(
                func.count(WorkUpdate.id).label("total"),
                func.sum(
                    case(
                        (
                            and_(
                                WorkUpdate.created_by_user_id.isnot(None),
                                WorkUpdate.created_by_user_id == Worker.user_id,
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("worker_authored"),
                func.sum(
                    case(
                        (
                            and_(
                                WorkUpdate.created_by_user_id.isnot(None),
                                WorkUpdate.created_by_user_id != Worker.user_id,
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("management_authored"),
            )
            .join(Task, WorkUpdate.task_id == Task.id)
            .join(Worker, WorkUpdate.worker_id == Worker.id)
            .filter(Task.project_id == project_id)
            .first()
        )
        return (
            result.total or 0,
            int(result.worker_authored or 0),
            int(result.management_authored or 0),
        )

    # ─── Worker ──────────────────────────────────────────────────────────────

    def get_worker_report(self, worker: Worker) -> WorkerPerformanceReport:
        today = date.today()
        wid = worker.id

        task_stats = (
            self.db.query(
                func.count(Task.id).label("total"),
                func.sum(case((Task.status == TaskStatusEnum.COMPLETED, 1), else_=0)).label("completed"),
                func.sum(case((Task.status == TaskStatusEnum.BLOCKED, 1), else_=0)).label("blocked"),
            )
            .filter(Task.assignee_id == wid)
            .first()
        )
        total_tasks = task_stats.total or 0
        completed_tasks = int(task_stats.completed or 0)
        blocked_tasks = int(task_stats.blocked or 0)
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0.0

        overdue_tasks = (
            self.db.query(func.count(Task.id))
            .filter(
                Task.assignee_id == wid,
                Task.status != TaskStatusEnum.COMPLETED,
                Task.due_date < today,
            )
            .scalar()
            or 0
        )

        # Activity — join through WorkUpdate.worker_id
        activity_result = (
            self.db.query(
                func.count(WorkUpdate.id).label("total"),
                func.sum(
                    case(
                        (
                            and_(
                                WorkUpdate.created_by_user_id.isnot(None),
                                WorkUpdate.created_by_user_id == worker.user_id,
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("worker_authored"),
                func.sum(
                    case(
                        (
                            and_(
                                WorkUpdate.created_by_user_id.isnot(None),
                                WorkUpdate.created_by_user_id != worker.user_id,
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("management_authored"),
            )
            .filter(WorkUpdate.worker_id == wid)
            .first()
        )
        total_updates = activity_result.total or 0
        worker_authored = int(activity_result.worker_authored or 0)
        mgmt_authored = int(activity_result.management_authored or 0)

        avg_ct = _cycle_time_hours(self.db, Task.assignee_id == wid)

        # Active projects = distinct project_ids among non-completed assigned tasks
        active_projects = (
            self.db.query(func.count(func.distinct(Task.project_id)))
            .filter(Task.assignee_id == wid, Task.status != TaskStatusEnum.COMPLETED)
            .scalar()
            or 0
        )

        user = self.db.query(User).filter(User.id == worker.user_id).first()
        worker_name = user.name if user else "Unknown"

        return WorkerPerformanceReport(
            metadata=self._metadata("worker"),
            worker_id=worker.id,
            worker_name=worker_name,
            worker_role=worker.role,
            worker_status=worker.status.value,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            overdue_tasks=overdue_tasks,
            blocked_tasks=blocked_tasks,
            completion_rate=completion_rate,
            total_updates=total_updates,
            worker_authored_updates=worker_authored,
            management_authored_updates=mgmt_authored,
            average_cycle_time_hours=avg_ct,
            active_projects=active_projects,
        )

    # ─── Team ────────────────────────────────────────────────────────────────

    def get_team_report(self, team: Team) -> TeamPerformanceReport:
        today = date.today()
        tid = team.id

        workforce = (
            self.db.query(
                func.count(Worker.id).label("total"),
                func.sum(case((Worker.status == WorkerStatusEnum.ACTIVE, 1), else_=0)).label("active"),
            )
            .filter(Worker.team_id == tid)
            .first()
        )
        total_workers = workforce.total or 0
        active_workers = int(workforce.active or 0)

        # Team tasks: tasks assigned to workers in this team
        worker_ids_sq = select(Worker.id).where(Worker.team_id == tid).scalar_subquery()

        task_stats = (
            self.db.query(
                func.count(Task.id).label("total"),
                func.sum(case((Task.status == TaskStatusEnum.COMPLETED, 1), else_=0)).label("completed"),
                func.sum(case((Task.status == TaskStatusEnum.BLOCKED, 1), else_=0)).label("blocked"),
            )
            .filter(Task.assignee_id.in_(worker_ids_sq))
            .first()
        )
        total_tasks = task_stats.total or 0
        completed_tasks = int(task_stats.completed or 0)
        blocked_tasks = int(task_stats.blocked or 0)
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0.0

        overdue_tasks = (
            self.db.query(func.count(Task.id))
            .filter(
                Task.assignee_id.in_(worker_ids_sq),
                Task.status != TaskStatusEnum.COMPLETED,
                Task.due_date < today,
            )
            .scalar()
            or 0
        )

        # Activity
        act_result = (
            self.db.query(
                func.count(WorkUpdate.id).label("total"),
                func.sum(
                    case(
                        (
                            and_(
                                WorkUpdate.created_by_user_id.isnot(None),
                                WorkUpdate.created_by_user_id == Worker.user_id,
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("worker_authored"),
                func.sum(
                    case(
                        (
                            and_(
                                WorkUpdate.created_by_user_id.isnot(None),
                                WorkUpdate.created_by_user_id != Worker.user_id,
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("management_authored"),
            )
            .join(Worker, WorkUpdate.worker_id == Worker.id)
            .filter(Worker.team_id == tid)
            .first()
        )
        total_updates = act_result.total or 0
        worker_authored = int(act_result.worker_authored or 0)
        mgmt_authored = int(act_result.management_authored or 0)

        avg_ct = _cycle_time_hours(self.db, Task.assignee_id.in_(worker_ids_sq))

        return TeamPerformanceReport(
            metadata=self._metadata("team"),
            team_id=team.id,
            team_name=team.name,
            total_workers=total_workers,
            active_workers=active_workers,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            overdue_tasks=overdue_tasks,
            blocked_tasks=blocked_tasks,
            completion_rate=completion_rate,
            total_updates=total_updates,
            worker_authored_updates=worker_authored,
            management_authored_updates=mgmt_authored,
            average_cycle_time_hours=avg_ct,
        )

    # ─── Activity ────────────────────────────────────────────────────────────

    def get_activity_report(
        self,
        worker_id: Optional[str] = None,
        project_id: Optional[str] = None,
        team_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ActivityReport:
        limit = min(limit, 100)

        # Build base query with all necessary joins
        q = (
            self.db.query(
                WorkUpdate.id.label("update_id"),
                WorkUpdate.task_id,
                Task.title.label("task_title"),
                WorkUpdate.worker_id,
                User.name.label("worker_name"),
                Task.project_id,
                Project.name.label("project_name"),
                WorkUpdate.description,
                WorkUpdate.timestamp,
                WorkUpdate.created_by_user_id,
                Worker.user_id.label("worker_user_id"),
            )
            .join(Task, WorkUpdate.task_id == Task.id)
            .join(Project, Task.project_id == Project.id)
            .join(Worker, WorkUpdate.worker_id == Worker.id)
            .join(User, Worker.user_id == User.id)
        )

        if worker_id:
            q = q.filter(WorkUpdate.worker_id == worker_id)
        if project_id:
            q = q.filter(Task.project_id == project_id)
        if team_id:
            q = q.filter(Worker.team_id == team_id)
        if start_date:
            q = q.filter(WorkUpdate.timestamp >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            q = q.filter(WorkUpdate.timestamp <= datetime.combine(end_date, datetime.max.time()))

        total = q.count()
        rows = q.order_by(WorkUpdate.timestamp.desc()).offset(offset).limit(limit).all()

        # Resolve authored_by names for management authors in one lookup
        mgmt_user_ids = {
            r.created_by_user_id
            for r in rows
            if r.created_by_user_id and r.created_by_user_id != r.worker_user_id
        }
        mgmt_names: dict[str, str] = {}
        if mgmt_user_ids:
            mgmt_users = self.db.query(User.id, User.name).filter(User.id.in_(mgmt_user_ids)).all()
            mgmt_names = {u.id: u.name for u in mgmt_users}

        items = []
        for r in rows:
            if r.created_by_user_id is None:
                authorship = "unknown"
                authored_by_name = None
            elif r.created_by_user_id == r.worker_user_id:
                authorship = "worker"
                authored_by_name = r.worker_name
            else:
                authorship = "management"
                authored_by_name = mgmt_names.get(r.created_by_user_id)

            items.append(
                ActivityReportItem(
                    update_id=r.update_id,
                    task_id=r.task_id,
                    task_title=r.task_title,
                    worker_id=r.worker_id,
                    worker_name=r.worker_name,
                    project_id=r.project_id,
                    project_name=r.project_name,
                    description=r.description,
                    timestamp=r.timestamp,
                    created_by_user_id=r.created_by_user_id,
                    authored_by_name=authored_by_name,
                    authorship=authorship,
                )
            )

        return ActivityReport(
            metadata=self._metadata("activity"),
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )
