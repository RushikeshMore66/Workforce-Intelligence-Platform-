from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from typing import Optional

from app.models.task import Task, TaskStatusEnum, WorkUpdate, TaskTransition
from app.models.user import Worker
from app.schemas.analytics import (
    WorkerWorkloadMetrics,
    WorkerActivityMetrics,
    WorkerDeliveryMetrics,
    WorkerAnalyticsOut,
)


class WorkerAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_worker_analytics(self, worker_id: str) -> WorkerAnalyticsOut:
        worker = self.db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            raise ValueError("Worker not found")

        workload = self._get_workload_metrics(worker_id)
        activity = self._get_activity_metrics(worker_id, worker.user_id)
        delivery = self._get_delivery_metrics(worker_id)

        return WorkerAnalyticsOut(
            worker_id=worker_id,
            workload=workload,
            activity=activity,
            delivery=delivery,
        )

    def _get_workload_metrics(self, worker_id: str) -> WorkerWorkloadMetrics:
        # Group by status to avoid N+1 and Python counting
        status_counts = self.db.query(
            Task.status, func.count(Task.id)
        ).filter(Task.assignee_id == worker_id).group_by(Task.status).all()

        counts = {status: count for status, count in status_counts}
        todo = counts.get(TaskStatusEnum.TODO, 0)
        in_progress = counts.get(TaskStatusEnum.IN_PROGRESS, 0)
        blocked = counts.get(TaskStatusEnum.BLOCKED, 0)
        completed = counts.get(TaskStatusEnum.COMPLETED, 0)
        total = todo + in_progress + blocked + completed

        overdue = self.db.query(func.count(Task.id)).filter(
            Task.assignee_id == worker_id,
            Task.status != TaskStatusEnum.COMPLETED,
            Task.due_date < date.today()
        ).scalar() or 0

        return WorkerWorkloadMetrics(
            total=total,
            todo=todo,
            in_progress=in_progress,
            blocked=blocked,
            completed=completed,
            overdue=overdue
        )

    def _get_activity_metrics(self, worker_id: str, user_id: str) -> WorkerActivityMetrics:
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)

        # Single aggregated query for all activity metrics
        result = self.db.query(
            func.count(WorkUpdate.id).label("total"),
            func.sum(case((WorkUpdate.timestamp >= seven_days_ago, 1), else_=0)).label("last_7"),
            func.sum(case((WorkUpdate.timestamp >= thirty_days_ago, 1), else_=0)).label("last_30"),
            func.max(WorkUpdate.timestamp).label("last_update_at"),
            func.sum(case((WorkUpdate.created_by_user_id == user_id, 1), else_=0)).label("worker_authored"),
            func.sum(case((WorkUpdate.created_by_user_id != user_id, 1), else_=0)).label("management_authored")
        ).filter(
            WorkUpdate.worker_id == worker_id
        ).first()

        return WorkerActivityMetrics(
            total_updates=result.total or 0,
            updates_last_7_days=int(result.last_7 or 0) if result.last_7 else 0,
            updates_last_30_days=int(result.last_30 or 0) if result.last_30 else 0,
            last_update_at=result.last_update_at,
            worker_authored_updates=int(result.worker_authored or 0) if result.worker_authored else 0,
            management_authored_updates=int(result.management_authored or 0) if result.management_authored else 0
        )

    def _get_delivery_metrics(self, worker_id: str) -> WorkerDeliveryMetrics:
        # Total tasks
        total_tasks = self.db.query(func.count(Task.id)).filter(Task.assignee_id == worker_id).scalar() or 0
        
        # Completed tasks
        completed_tasks = self.db.query(func.count(Task.id)).filter(
            Task.assignee_id == worker_id, 
            Task.status == TaskStatusEnum.COMPLETED
        ).scalar() or 0

        completion_rate = (completed_tasks / total_tasks) if total_tasks > 0 else 0.0

        # Cycle time: targeted aggregation avoiding N+1
        # CTE to get the first TODO -> IN_PROGRESS transition per task
        started_cte = self.db.query(
            TaskTransition.task_id,
            func.min(TaskTransition.timestamp).label("started_at")
        ).filter(
            TaskTransition.from_status == TaskStatusEnum.TODO,
            TaskTransition.to_status == TaskStatusEnum.IN_PROGRESS
        ).group_by(TaskTransition.task_id).cte("started_cte")

        # CTE to get the first transition to COMPLETED per task
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
            Task.assignee_id == worker_id
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

        return WorkerDeliveryMetrics(
            completed_tasks=completed_tasks,
            completion_rate=completion_rate,
            cycle_time=cycle_time
        )
