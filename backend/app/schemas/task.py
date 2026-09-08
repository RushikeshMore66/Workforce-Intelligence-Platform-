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
    status: Optional[TaskStatus] = None
    priority: Optional[ProjectPriority] = None
    due_date: Optional[date] = None


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
