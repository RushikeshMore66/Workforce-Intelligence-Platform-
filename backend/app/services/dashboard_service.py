from datetime import date
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.blocker import Blocker, BlockerStatusEnum
from app.models.project import Project, ProjectStatusEnum, ProjectHealthEnum
from app.models.task import Task, TaskStatusEnum
from app.models.user import Worker, WorkerStatusEnum
from app.schemas.dashboard import AttentionItemOut, DashboardMetricsOut


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_metrics(self) -> DashboardMetricsOut:
        total_workers = self.db.query(Worker).count()
        workers_active = self.db.query(Worker).filter(Worker.status == WorkerStatusEnum.ACTIVE).count()
        workers_on_leave = self.db.query(Worker).filter(Worker.status == WorkerStatusEnum.ON_LEAVE).count()
        workers_unavailable = self.db.query(Worker).filter(Worker.status == WorkerStatusEnum.UNAVAILABLE).count()

        active_projects = self.db.query(Project).filter(Project.status == ProjectStatusEnum.ACTIVE).count()
        completed_projects = self.db.query(Project).filter(Project.status == ProjectStatusEnum.COMPLETED).count()
        projects_on_track = (
            self.db.query(Project)
            .filter(Project.status == ProjectStatusEnum.ACTIVE, Project.health == ProjectHealthEnum.ON_TRACK)
            .count()
        )
        projects_at_risk = (
            self.db.query(Project)
            .filter(Project.status == ProjectStatusEnum.ACTIVE, Project.health == ProjectHealthEnum.AT_RISK)
            .count()
        )
        projects_delayed = (
            self.db.query(Project)
            .filter(Project.status == ProjectStatusEnum.ACTIVE, Project.health == ProjectHealthEnum.DELAYED)
            .count()
        )

        tasks_completed = self.db.query(Task).filter(Task.status == TaskStatusEnum.COMPLETED).count()
        tasks_in_progress = self.db.query(Task).filter(Task.status == TaskStatusEnum.IN_PROGRESS).count()
        tasks_pending = self.db.query(Task).filter(Task.status == TaskStatusEnum.PLANNED).count()
        tasks_blocked = self.db.query(Task).filter(Task.status == TaskStatusEnum.ON_HOLD).count()

        return DashboardMetricsOut(
            active_projects=active_projects,
            completed_projects=completed_projects,
            total_workers=total_workers,
            workers_active=workers_active,
            workers_on_leave=workers_on_leave,
            workers_unavailable=workers_unavailable,
            tasks_completed=tasks_completed,
            tasks_in_progress=tasks_in_progress,
            tasks_pending=tasks_pending,
            tasks_blocked=tasks_blocked,
            projects_on_track=projects_on_track,
            projects_at_risk=projects_at_risk,
            projects_delayed=projects_delayed,
        )

    def get_attention_items(self) -> List[AttentionItemOut]:
        """
        Compute attention items from real database state.
        Returns up to 5 highest-priority items.
        """
        items: List[AttentionItemOut] = []
        today = date.today()

        # 1. Active projects that are past deadline
        overdue_projects = (
            self.db.query(Project)
            .filter(
                Project.status == ProjectStatusEnum.ACTIVE,
                Project.deadline < today,
            )
            .limit(2)
            .all()
        )
        for p in overdue_projects:
            days_over = (today - p.deadline).days
            items.append(
                AttentionItemOut(
                    id=f"att-overdue-{p.id}",
                    type="DEADLINE",
                    title=f'"{p.name}" is past its deadline',
                    description=(
                        f"Deadline was {p.deadline.strftime('%d %b %Y')} "
                        f"({days_over} day{'s' if days_over != 1 else ''} ago). "
                        f"Current progress: {p.progress}%. Status: {p.status.value}."
                    ),
                    priority="HIGH",
                    project_id=p.id,
                )
            )

        # 2. Active DELAYED projects
        delayed_projects = (
            self.db.query(Project)
            .filter(
                Project.status == ProjectStatusEnum.ACTIVE,
                Project.health == ProjectHealthEnum.DELAYED,
                Project.deadline >= today,  # not already caught above
            )
            .limit(2)
            .all()
        )
        for p in delayed_projects:
            items.append(
                AttentionItemOut(
                    id=f"att-delayed-{p.id}",
                    type="RISK",
                    title=f'"{p.name}" is marked DELAYED',
                    description=(
                        f"Progress: {p.progress}%. Deadline: {p.deadline.strftime('%d %b %Y')}. "
                        f"Intervention may be required."
                    ),
                    priority="HIGH",
                    project_id=p.id,
                )
            )

        # 3. Projects with open blockers
        if len(items) < 5:
            # Get project ids that have open blockers, excluding ones already added
            already_ids = {i.project_id for i in items if i.project_id}
            blocker_projects = (
                self.db.query(Project.id, Project.name, func.count(Blocker.id).label("blocker_count"))
                .join(Blocker, Blocker.project_id == Project.id)
                .filter(
                    Blocker.status == BlockerStatusEnum.OPEN,
                    Project.status == ProjectStatusEnum.ACTIVE,
                )
                .group_by(Project.id, Project.name)
                .having(func.count(Blocker.id) > 0)
                .limit(3)
                .all()
            )
            for row in blocker_projects:
                if row.id not in already_ids and len(items) < 5:
                    n = row.blocker_count
                    items.append(
                        AttentionItemOut(
                            id=f"att-blocker-{row.id}",
                            type="BLOCKER",
                            title=f'"{row.name}" has {n} open blocker{"s" if n != 1 else ""}',
                            description=(
                                f"{n} unresolved blocker{'s' if n != 1 else ''} "
                                f"may be impacting delivery."
                            ),
                            priority="HIGH" if n >= 2 else "MEDIUM",
                            project_id=row.id,
                        )
                    )

        # 4. AT_RISK projects (not already captured)
        if len(items) < 5:
            already_ids = {i.project_id for i in items if i.project_id}
            at_risk = (
                self.db.query(Project)
                .filter(
                    Project.status == ProjectStatusEnum.ACTIVE,
                    Project.health == ProjectHealthEnum.AT_RISK,
                    Project.id.notin_(already_ids),
                )
                .limit(5 - len(items))
                .all()
            )
            for p in at_risk:
                items.append(
                    AttentionItemOut(
                        id=f"att-risk-{p.id}",
                        type="RISK",
                        title=f'"{p.name}" is at risk',
                        description=(
                            f"Project health is AT_RISK. Progress: {p.progress}%. "
                            f"Deadline: {p.deadline.strftime('%d %b %Y')}."
                        ),
                        priority="MEDIUM",
                        project_id=p.id,
                    )
                )

        return items[:5]
