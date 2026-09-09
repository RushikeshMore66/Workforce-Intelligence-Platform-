from typing import List
from app.schemas.common import BaseSchema


class TaskCompletionDataPoint(BaseSchema):
    month: str
    completed: int
    in_progress: int
    blocked: int


class TeamWorkloadDataPoint(BaseSchema):
    team: str
    tasks: int
    completed: int
    blocked: int


class ProjectProgressDataPoint(BaseSchema):
    name: str
    progress: int
    target: int


class WorkloadTrendPoint(BaseSchema):
    week: str
    backend: int
    frontend: int
    qa: int
    devops: int
    uiux: int


class AnalyticsDataOut(BaseSchema):
    task_completion: List[TaskCompletionDataPoint]
    team_workload: List[TeamWorkloadDataPoint]
    project_progress: List[ProjectProgressDataPoint]
    workload_trend: List[WorkloadTrendPoint]


class WorkerWorkloadMetrics(BaseSchema):
    total: int
    todo: int
    in_progress: int
    blocked: int
    completed: int
    overdue: int


class WorkerActivityMetrics(BaseSchema):
    total_updates: int
    updates_last_7_days: int
    updates_last_30_days: int
    last_update_at: str | None = None
    worker_authored_updates: int
    management_authored_updates: int


class WorkerDeliveryMetrics(BaseSchema):
    completed_tasks: int
    completion_rate: float
    cycle_time: float | None = None


class WorkerAnalyticsOut(BaseSchema):
    worker_id: str
    workload: WorkerWorkloadMetrics
    activity: WorkerActivityMetrics
    delivery: WorkerDeliveryMetrics
