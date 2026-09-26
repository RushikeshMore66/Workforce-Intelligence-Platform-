from datetime import date, datetime
from typing import Optional
from app.schemas.common import BaseSchema, TaskStatus, ProjectPriority


class TaskBase(BaseSchema):
    project_id: str
    title: str
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    team_id: Optional[str] = None
    priority: ProjectPriority = ProjectPriority.MEDIUM
    due_date: date


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    team_id: Optional[str] = None
    priority: Optional[ProjectPriority] = None
    due_date: Optional[date] = None
    # Status is intentionally excluded — use POST /{task_id}/status instead.


class TaskStatusChange(BaseSchema):
    """Request body for the dedicated task status-transition endpoint."""
    status: TaskStatus
    reason: Optional[str] = None


class TaskOut(TaskBase):
    id: str
    status: TaskStatus
    created_at: datetime


class WorkUpdateCreate(BaseSchema):
    description: str


class WorkUpdateOut(BaseSchema):
    id: str
    task_id: str
    worker_id: str
    created_by_user_id: Optional[str] = None
    description: str
    timestamp: datetime
