from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.task import Task, TaskStatusEnum, WorkUpdate, TaskTransition
from app.models.user import Worker, WorkerStatusEnum
from app.models.team import Team, team_projects
from app.schemas.analytics import (
    ProjectWorkforceMetrics,
    ProjectWorkloadMetrics,
    ProjectActivityMetrics,
    ProjectDeliveryMetrics,
    ProjectAnalyticsOut,
)


class ProjectAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_project_analytics(self, project_id: str) -> ProjectAnalyticsOut:
        workforce = self._get_workforce_metrics(project_id)
        workload = self._get_workload_metrics(project_id)
        activity = self._get_activity_metrics(project_id)
        delivery = self._get_delivery_metrics(project_id)

        return ProjectAnalyticsOut(
            project_id=project_id,
            workforce=workforce,
            workload=workload,
            activity=activity,
            delivery=delivery,
        )

    def _get_workforce_metrics(self, project_id: str) -> ProjectWorkforceMetrics:
        # Official project workforce comes from TeamProject -> Team -> Worker
        workers_query = self.db.query(
            func.count(Worker.id).label("total"),
            func.sum(case((Worker.status == WorkerStatusEnum.ACTIVE, 1), else_=0)).label("active")
        ).join(
            Team, Worker.team_id == Team.id
        ).join(
            team_projects, Team.id == team_projects.c.team_id
        ).filter(
            team_projects.c.project_id == project_id
        ).first()

        total_workers = workers_query.total or 0
        active_workers = int(workers_query.active or 0)

        # Workers with tasks represents actual task participation
        workers_with_tasks = self.db.query(
            func.count(func.distinct(Task.assignee_id))
        ).filter(
            Task.project_id == project_id,
            Task.assignee_id.isnot(None)
        ).scalar() or 0

        return ProjectWorkforceMetrics(
            total_workers=total_workers,
            active_workers=active_workers,
            workers_with_tasks=workers_with_tasks,
        )

    def _get_workload_metrics(self, project_id: str) -> ProjectWorkloadMetrics:
        status_counts = self.db.query(
            Task.status, func.count(Task.id)
        ).filter(
            Task.project_id == project_id
        ).group_by(Task.status).all()

        counts = {status: count for status, count in status_counts}
        todo = counts.get(TaskStatusEnum.TODO, 0)
        in_progress = counts.get(TaskStatusEnum.IN_PROGRESS, 0)
        blocked = counts.get(TaskStatusEnum.BLOCKED, 0)
        completed = counts.get(TaskStatusEnum.COMPLETED, 0)
        total = todo + in_progress + blocked + completed

        overdue = self.db.query(func.count(Task.id)).filter(
            Task.project_id == project_id,
            Task.status != TaskStatusEnum.COMPLETED,
            Task.due_date < date.today()
        ).scalar() or 0

        return ProjectWorkloadMetrics(
            total=total,
            todo=todo,
            in_progress=in_progress,
            blocked=blocked,
            completed=completed,
            overdue=overdue
        )

    def _get_activity_metrics(self, project_id: str) -> ProjectActivityMetrics:
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)

        # Aggregate updates for all tasks in the project
        result = self.db.query(
            func.count(WorkUpdate.id).label("total"),
            func.sum(case((WorkUpdate.timestamp >= seven_days_ago, 1), else_=0)).label("last_7"),
            func.sum(case((WorkUpdate.timestamp >= thirty_days_ago, 1), else_=0)).label("last_30"),
            func.max(WorkUpdate.timestamp).label("last_update_at"),
            func.sum(case((WorkUpdate.created_by_user_id == Worker.user_id, 1), else_=0)).label("worker_authored"),
            func.sum(case((WorkUpdate.created_by_user_id != Worker.user_id, 1), else_=0)).label("management_authored")
        ).join(
            Task, WorkUpdate.task_id == Task.id
        ).join(
            Worker, WorkUpdate.worker_id == Worker.id
        ).filter(
            Task.project_id == project_id
        ).first()

        return ProjectActivityMetrics(
            total_updates=result.total or 0,
            updates_last_7_days=int(result.last_7 or 0) if result.last_7 else 0,
            updates_last_30_days=int(result.last_30 or 0) if result.last_30 else 0,
            last_update_at=result.last_update_at,
            worker_authored_updates=int(result.worker_authored or 0) if result.worker_authored else 0,
            management_authored_updates=int(result.management_authored or 0) if result.management_authored else 0
        )

    def _get_delivery_metrics(self, project_id: str) -> ProjectDeliveryMetrics:
        # Total tasks and completed tasks for the project
        task_stats = self.db.query(
            func.count(Task.id).label("total"),
            func.sum(case((Task.status == TaskStatusEnum.COMPLETED, 1), else_=0)).label("completed")
        ).filter(
            Task.project_id == project_id
        ).first()

        total_tasks = task_stats.total or 0
        completed_tasks = int(task_stats.completed or 0) if task_stats.completed else 0
        completion_rate = (completed_tasks / total_tasks) if total_tasks > 0 else 0.0

        # Cycle time calculation using CTEs
        started_cte = self.db.query(
            TaskTransition.task_id,
            func.min(TaskTransition.timestamp).label("started_at")
        ).filter(
            TaskTransition.from_status == TaskStatusEnum.TODO,
            TaskTransition.to_status == TaskStatusEnum.IN_PROGRESS
        ).group_by(TaskTransition.task_id).cte("started_cte")

        completed_cte = self.db.query(
            TaskTransition.task_id,
            func.min(TaskTransition.timestamp).label("completed_at")
        ).filter(
            TaskTransition.to_status == TaskStatusEnum.COMPLETED
        ).group_by(TaskTransition.task_id).cte("completed_cte")

        query = self.db.query(
            started_cte.c.started_at,
            completed_cte.c.completed_at
        ).join(
            completed_cte, started_cte.c.task_id == completed_cte.c.task_id
        ).join(
            Task, Task.id == started_cte.c.task_id
        ).filter(
            Task.project_id == project_id
        )

        valid_transitions = query.all()
        
        cycle_time = None
        if valid_transitions:
            total_duration = sum(
                (comp - start).total_seconds() 
                for start, comp in valid_transitions 
                if comp > start
            )
            count = len(valid_transitions)
            if count > 0:
                cycle_time = total_duration / count

        return ProjectDeliveryMetrics(
            completed_tasks=completed_tasks,
            completion_rate=completion_rate,
            average_cycle_time=cycle_time
        )
