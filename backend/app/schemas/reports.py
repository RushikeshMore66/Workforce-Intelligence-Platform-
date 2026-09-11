"""
Report schemas for the Workforce Intelligence Platform.

Metric definitions:
- completion_rate = completed_tasks / total_tasks (0.0 if total_tasks == 0)
- average_cycle_time_hours: average of (first COMPLETED timestamp - first TODO→IN_PROGRESS
  timestamp) across completed tasks that have both transitions. NULL if no valid pairs.
- worker_authored_updates: created_by_user_id == worker's user_id (NULL excluded)
- management_authored_updates: created_by_user_id IS NOT NULL AND != worker's user_id
"""

from datetime import date, datetime
from typing import List, Optional

from app.schemas.common import BaseSchema


class ReportMetadata(BaseSchema):
    generated_at: datetime
    report_type: str


class OrganizationSummaryReport(BaseSchema):
    metadata: ReportMetadata
    total_workers: int
    active_workers: int
    total_teams: int
    total_projects: int
    active_projects: int
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    overdue_tasks: int
    blocked_tasks: int
    unassigned_tasks: int


class ProjectPerformanceReport(BaseSchema):
    metadata: ReportMetadata
    project_id: str
    project_name: str
    project_status: str
    project_health: str
    # Workload
    total_tasks: int
    todo_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    completed_tasks: int
    overdue_tasks: int
    unassigned_tasks: int
    # Activity
    total_updates: int
    worker_authored_updates: int
    management_authored_updates: int
    # Delivery
    completion_rate: float
    average_cycle_time_hours: Optional[float] = None


class WorkerPerformanceReport(BaseSchema):
    metadata: ReportMetadata
    worker_id: str
    worker_name: str
    worker_role: str
    worker_status: str
    # Tasks
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    blocked_tasks: int
    completion_rate: float
    # Activity
    total_updates: int
    worker_authored_updates: int
    management_authored_updates: int
    # Delivery
    average_cycle_time_hours: Optional[float] = None
    # Context
    active_projects: int


class TeamPerformanceReport(BaseSchema):
    metadata: ReportMetadata
    team_id: str
    team_name: str
    # Workforce
    total_workers: int
    active_workers: int
    # Tasks
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    blocked_tasks: int
    completion_rate: float
    # Activity
    total_updates: int
    worker_authored_updates: int
    management_authored_updates: int
    # Delivery
    average_cycle_time_hours: Optional[float] = None


class ActivityReportItem(BaseSchema):
    update_id: str
    task_id: str
    task_title: str
    worker_id: str
    worker_name: str
    project_id: str
    project_name: str
    description: str
    timestamp: datetime
    created_by_user_id: Optional[str] = None
    authored_by_name: Optional[str] = None
    authorship: str  # "worker", "management", or "unknown"


class ActivityReport(BaseSchema):
    metadata: ReportMetadata
    total: int
    limit: int
    offset: int
    items: List[ActivityReportItem]
