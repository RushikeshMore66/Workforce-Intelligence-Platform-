from typing import List
from datetime import datetime
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


class TeamWorkforceMetrics(BaseSchema):
    total_workers: int
    active_workers: int
    workers_with_tasks: int
    workers_with_overdue_tasks: int


class TeamWorkloadMetrics(BaseSchema):
    total: int
    todo: int
    in_progress: int
    blocked: int
    completed: int
    overdue: int


class TeamActivityMetrics(BaseSchema):
    total_updates: int
    updates_last_7_days: int
    updates_last_30_days: int
    last_update_at: str | None = None
    worker_authored_updates: int
    management_authored_updates: int


class TeamDeliveryMetrics(BaseSchema):
    completed_tasks: int
    completion_rate: float
    average_cycle_time: float | None = None


class TeamAnalyticsOut(BaseSchema):
    team_id: str
    workforce: TeamWorkforceMetrics
    workload: TeamWorkloadMetrics
    activity: TeamActivityMetrics
    delivery: TeamDeliveryMetrics


class ProjectWorkforceMetrics(BaseSchema):
    total_workers: int
    active_workers: int
    workers_with_tasks: int


class ProjectWorkloadMetrics(BaseSchema):
    total: int
    todo: int
    in_progress: int
    blocked: int
    completed: int
    overdue: int


class ProjectActivityMetrics(BaseSchema):
    total_updates: int
    updates_last_7_days: int
    updates_last_30_days: int
    last_update_at: datetime | None = None
    worker_authored_updates: int
    management_authored_updates: int


class ProjectDeliveryMetrics(BaseSchema):
    completed_tasks: int
    completion_rate: float
    average_cycle_time: float | None = None


class ProjectAnalyticsOut(BaseSchema):
    project_id: str
    workforce: ProjectWorkforceMetrics
    workload: ProjectWorkloadMetrics
    activity: ProjectActivityMetrics
    delivery: ProjectDeliveryMetrics


class OrganizationWorkforceMetrics(BaseSchema):
    total_workers: int
    active_workers: int
    workers_with_tasks: int
    workers_without_tasks: int
    total_teams: int
    active_teams: int
    total_projects: int
    active_projects: int


class OrganizationWorkloadMetrics(BaseSchema):
    total: int
    todo: int
    in_progress: int
    blocked: int
    completed: int
    overdue: int
    unassigned: int


class OrganizationActivityMetrics(BaseSchema):
    total_updates: int
    updates_last_7_days: int
    updates_last_30_days: int
    last_update_at: datetime | None = None
    worker_authored_updates: int
    management_authored_updates: int


class OrganizationDeliveryMetrics(BaseSchema):
    completed_tasks: int
    completion_rate: float
    average_cycle_time_hours: float | None = None  # Documented as hours
    tasks_with_valid_transition_history: int
    tasks_missing_transition_history: int


class OrganizationAttentionMetrics(BaseSchema):
    overdue_tasks: int
    blocked_tasks: int
    unassigned_tasks: int
    at_risk_projects: int
    workers_with_no_recent_activity: int


class OrganizationAnalyticsOut(BaseSchema):
    workforce: OrganizationWorkforceMetrics
    workload: OrganizationWorkloadMetrics
    activity: OrganizationActivityMetrics
    delivery: OrganizationDeliveryMetrics
    attention: OrganizationAttentionMetrics
