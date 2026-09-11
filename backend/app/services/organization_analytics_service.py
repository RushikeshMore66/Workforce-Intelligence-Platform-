from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_

from app.models.task import Task, TaskStatusEnum, WorkUpdate, TaskTransition
from app.models.user import Worker, WorkerStatusEnum
from app.models.team import Team
from app.models.project import Project, ProjectStatusEnum, ProjectHealthEnum
from app.schemas.analytics import (
    OrganizationWorkforceMetrics,
    OrganizationWorkloadMetrics,
    OrganizationActivityMetrics,
    OrganizationDeliveryMetrics,
    OrganizationAttentionMetrics,
    OrganizationAnalyticsOut,
)


class OrganizationAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_organization_analytics(self) -> OrganizationAnalyticsOut:
        now = datetime.utcnow()
        cutoff_7 = now - timedelta(days=7)
        cutoff_30 = now - timedelta(days=30)
        today = date.today()

        workforce = self._get_workforce_metrics()
        workload = self._get_workload_metrics(today)
        activity = self._get_activity_metrics(cutoff_7, cutoff_30)
        delivery = self._get_delivery_metrics()
        attention = self._get_attention_metrics(cutoff_7, workload)

        return OrganizationAnalyticsOut(
            workforce=workforce,
            workload=workload,
            activity=activity,
            delivery=delivery,
            attention=attention,
        )

    def _get_workforce_metrics(self) -> OrganizationWorkforceMetrics:
        # Worker metrics
        worker_stats = self.db.query(
            func.count(Worker.id).label("total"),
            func.sum(case((Worker.status == WorkerStatusEnum.ACTIVE, 1), else_=0)).label("active")
        ).first()

        total_workers = worker_stats.total or 0
        active_workers = int(worker_stats.active or 0)

        workers_with_tasks = self.db.query(
            func.count(func.distinct(Task.assignee_id))
        ).filter(
            Task.assignee_id.isnot(None)
        ).scalar() or 0

        workers_without_tasks = total_workers - workers_with_tasks

        # Team metrics
        total_teams = self.db.query(func.count(Team.id)).scalar() or 0
        
        # active_teams is a proxy: Teams with at least one worker
        active_teams = self.db.query(
            func.count(func.distinct(Worker.team_id))
        ).filter(
            Worker.team_id.isnot(None)
        ).scalar() or 0

        # Project metrics
        project_stats = self.db.query(
            func.count(Project.id).label("total"),
            func.sum(case((Project.status == ProjectStatusEnum.ACTIVE, 1), else_=0)).label("active")
        ).first()

        total_projects = project_stats.total or 0
        active_projects = int(project_stats.active or 0)

        return OrganizationWorkforceMetrics(
            total_workers=total_workers,
            active_workers=active_workers,
            workers_with_tasks=workers_with_tasks,
            workers_without_tasks=workers_without_tasks,
            total_teams=total_teams,
            active_teams=active_teams,
            total_projects=total_projects,
            active_projects=active_projects,
        )

    def _get_workload_metrics(self, today: date) -> OrganizationWorkloadMetrics:
        status_counts = self.db.query(
            Task.status, func.count(Task.id)
        ).group_by(Task.status).all()

        counts = {status: count for status, count in status_counts}
        todo = counts.get(TaskStatusEnum.TODO, 0)
        in_progress = counts.get(TaskStatusEnum.IN_PROGRESS, 0)
        blocked = counts.get(TaskStatusEnum.BLOCKED, 0)
        completed = counts.get(TaskStatusEnum.COMPLETED, 0)
        total = todo + in_progress + blocked + completed

        overdue = self.db.query(func.count(Task.id)).filter(
            Task.status != TaskStatusEnum.COMPLETED,
            Task.due_date < today
        ).scalar() or 0

        unassigned = self.db.query(func.count(Task.id)).filter(
            Task.assignee_id.is_(None)
        ).scalar() or 0

        return OrganizationWorkloadMetrics(
            total=total,
            todo=todo,
            in_progress=in_progress,
            blocked=blocked,
            completed=completed,
            overdue=overdue,
            unassigned=unassigned,
        )

    def _get_activity_metrics(self, cutoff_7: datetime, cutoff_30: datetime) -> OrganizationActivityMetrics:
        # Treat created_by_user_id IS NULL as unknown (neither worker nor management)
        result = self.db.query(
            func.count(WorkUpdate.id).label("total"),
            func.sum(case((WorkUpdate.timestamp >= cutoff_7, 1), else_=0)).label("last_7"),
            func.sum(case((WorkUpdate.timestamp >= cutoff_30, 1), else_=0)).label("last_30"),
            func.max(WorkUpdate.timestamp).label("last_update_at"),
            func.sum(case((and_(WorkUpdate.created_by_user_id.isnot(None), WorkUpdate.created_by_user_id == Worker.user_id), 1), else_=0)).label("worker_authored"),
            func.sum(case((and_(WorkUpdate.created_by_user_id.isnot(None), WorkUpdate.created_by_user_id != Worker.user_id), 1), else_=0)).label("management_authored")
        ).join(
            Worker, WorkUpdate.worker_id == Worker.id
        ).first()

        return OrganizationActivityMetrics(
            total_updates=result.total or 0,
            updates_last_7_days=int(result.last_7 or 0) if result.last_7 else 0,
            updates_last_30_days=int(result.last_30 or 0) if result.last_30 else 0,
            last_update_at=result.last_update_at,
            worker_authored_updates=int(result.worker_authored or 0) if result.worker_authored else 0,
            management_authored_updates=int(result.management_authored or 0) if result.management_authored else 0,
        )

    def _get_delivery_metrics(self) -> OrganizationDeliveryMetrics:
        # Delivery applies to ALL completed tasks in the organization
        task_stats = self.db.query(
            func.count(Task.id).label("total"),
            func.sum(case((Task.status == TaskStatusEnum.COMPLETED, 1), else_=0)).label("completed")
        ).first()

        total_tasks = task_stats.total or 0
        completed_tasks = int(task_stats.completed or 0) if task_stats.completed else 0
        completion_rate = (completed_tasks / total_tasks) if total_tasks > 0 else 0.0

        # Cycle time:
        # 1. First TODO -> IN_PROGRESS transition
        started_cte = self.db.query(
            TaskTransition.task_id,
            func.min(TaskTransition.timestamp).label("started_at")
        ).filter(
            TaskTransition.from_status == TaskStatusEnum.TODO,
            TaskTransition.to_status == TaskStatusEnum.IN_PROGRESS
        ).group_by(TaskTransition.task_id).cte("started_cte")

        # 2. First transition into COMPLETED
        completed_cte = self.db.query(
            TaskTransition.task_id,
            func.min(TaskTransition.timestamp).label("completed_at")
        ).filter(
            TaskTransition.to_status == TaskStatusEnum.COMPLETED
        ).group_by(TaskTransition.task_id).cte("completed_cte")

        # 3. Inner join for cycle time, ONLY for tasks currently COMPLETED
        query = self.db.query(
            started_cte.c.started_at,
            completed_cte.c.completed_at
        ).join(
            completed_cte, started_cte.c.task_id == completed_cte.c.task_id
        ).join(
            Task, Task.id == started_cte.c.task_id
        ).filter(
            Task.status == TaskStatusEnum.COMPLETED
        )

        valid_transitions = query.all()
        
        cycle_time_hours = None
        tasks_with_valid_history = 0
        if valid_transitions:
            total_seconds = sum(
                (comp - start).total_seconds() 
                for start, comp in valid_transitions 
                if comp > start
            )
            tasks_with_valid_history = len(valid_transitions)
            if tasks_with_valid_history > 0:
                cycle_time_hours = total_seconds / 3600.0 / tasks_with_valid_history

        tasks_missing_history = completed_tasks - tasks_with_valid_history

        return OrganizationDeliveryMetrics(
            completed_tasks=completed_tasks,
            completion_rate=completion_rate,
            average_cycle_time_hours=cycle_time_hours,
            tasks_with_valid_transition_history=tasks_with_valid_history,
            tasks_missing_transition_history=tasks_missing_history,
        )

    def _get_attention_metrics(self, cutoff_7: datetime, workload: OrganizationWorkloadMetrics) -> OrganizationAttentionMetrics:
        # Overdue, blocked, unassigned pulled from workload
        overdue_tasks = workload.overdue
        blocked_tasks = workload.blocked
        unassigned_tasks = workload.unassigned

        at_risk_projects = self.db.query(func.count(Project.id)).filter(
            Project.health.in_([ProjectHealthEnum.DELAYED, ProjectHealthEnum.AT_RISK])
        ).scalar() or 0

        # Workers with no activity in the last 7 days
        recent_update_worker_ids = self.db.query(WorkUpdate.worker_id).filter(
            WorkUpdate.timestamp >= cutoff_7
        )
        
        workers_with_no_recent_activity = self.db.query(func.count(Worker.id)).filter(
            Worker.id.notin_(recent_update_worker_ids)
        ).scalar() or 0

        return OrganizationAttentionMetrics(
            overdue_tasks=overdue_tasks,
            blocked_tasks=blocked_tasks,
            unassigned_tasks=unassigned_tasks,
            at_risk_projects=at_risk_projects,
            workers_with_no_recent_activity=workers_with_no_recent_activity,
        )
