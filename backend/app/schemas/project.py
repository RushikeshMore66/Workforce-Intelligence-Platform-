from datetime import date, datetime
from typing import Optional, List
from app.schemas.common import BaseSchema, ProjectStatus, ProjectHealth, ProjectPriority


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
    status: Optional[ProjectStatus] = None
    health: Optional[ProjectHealth] = None
    progress: Optional[int] = None


class ProjectOut(ProjectBase):
    id: str
    status: ProjectStatus
    health: ProjectHealth
    progress: int
    team_count: int
    created_at: datetime


class ProjectDetailOut(ProjectOut):
    team_ids: List[str] = []
