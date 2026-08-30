from typing import Optional, List
from pydantic import EmailStr
from app.schemas.common import BaseSchema, UserRole, WorkerStatus


class UserBase(BaseSchema):
    email: EmailStr
    name: str
    role: UserRole
    avatar_initials: str
    company: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: str


class SupervisorOut(BaseSchema):
    id: str
    user_id: str
    name: str
    email: str
    avatar_initials: str
    project_ids: List[str] = []
    team_ids: List[str] = []


class TeamLeaderOut(BaseSchema):
    id: str
    user_id: str
    name: str
    email: str
    avatar_initials: str
    team_id: Optional[str] = None


class WorkerOut(BaseSchema):
    id: str
    name: str
    email: str
    role: str
    team_id: Optional[str] = None
    team_leader_id: Optional[str] = None
    supervisor_id: Optional[str] = None
    avatar_initials: str
    status: WorkerStatus
    active_project_id: Optional[str] = None
    completed_task_count: int = 0
    in_progress_task_count: int = 0
    pending_task_count: int = 0
    blocked_task_count: int = 0
