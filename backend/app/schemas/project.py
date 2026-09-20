from datetime import date, datetime
from typing import List, Optional

from app.schemas.common import BaseSchema, ProjectHealth, ProjectPriority, ProjectStatus


class ProjectBase(BaseSchema):
    name: str
    client: str
    description: Optional[str] = None
    start_date: date
    deadline: date
    priority: ProjectPriority
    supervisor_id: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseSchema):
    name: Optional[str] = None
    client: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    priority: Optional[ProjectPriority] = None
    supervisor_id: Optional[str] = None
    health: Optional[ProjectHealth] = None
    # Project status and progress are workflow/derived fields.
    # They must not be directly patched from the generic update endpoint.


class ProjectStatusChange(BaseSchema):
    status: ProjectStatus
    reason: Optional[str] = None


class ProjectOut(ProjectBase):
    id: str
    status: ProjectStatus
    health: ProjectHealth
    progress: int
    team_count: int
    created_at: datetime


class ProjectDetailOut(ProjectOut):
    team_ids: List[str] = []
