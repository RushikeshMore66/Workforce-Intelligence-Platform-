from typing import Optional
from app.schemas.common import BaseSchema


class DashboardMetricsOut(BaseSchema):
    active_projects: int
    completed_projects: int
    total_workers: int
    workers_active: int
    workers_on_leave: int
    workers_unavailable: int
    tasks_completed: int
    tasks_in_progress: int
    tasks_pending: int
    tasks_blocked: int
    projects_on_track: int
    projects_at_risk: int
    projects_delayed: int


class AttentionItemOut(BaseSchema):
    id: str
    title: str
    description: str
    priority: str  # LOW, MEDIUM, HIGH
    project_id: Optional[str] = None
    type: str  # RISK, DEADLINE, BLOCKER, OVERLOAD, REVIEW
