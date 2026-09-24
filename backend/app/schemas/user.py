"""Pydantic schemas for user management (owner-facing CRUD) and role profiles.

These schemas define exactly what the owner API accepts and returns.
They deliberately exclude sensitive fields such as hashed_password.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import EmailStr, field_validator
from app.schemas.common import BaseSchema, UserRole, WorkerStatus


# ── Input schemas ──────────────────────────────────────────────────────────────


class WorkerProfileCreate(BaseSchema):
    """Role-specific data required when creating a WORKER account."""
    job_title: str  # stored in Worker.role (job description field)
    team_id: Optional[str] = None
    team_leader_id: Optional[str] = None
    supervisor_id: Optional[str] = None
    status: WorkerStatus = WorkerStatus.ACTIVE


class SupervisorProfileCreate(BaseSchema):
    """Role-specific data required when creating a SUPERVISOR account.

    The supervisor model currently has no additional profile fields beyond
    the user association; this placeholder allows future expansion.
    """
    pass


class TeamLeaderProfileCreate(BaseSchema):
    """Role-specific data required when creating a TEAM_LEADER account."""
    team_id: Optional[str] = None


class UserCreate(BaseSchema):
    """Validated input for creating a new user account.

    The owner provides role, basic identity, and role-specific profile data.
    Password must be at least 8 characters and is hashed server-side.
    Role cannot be set to OWNER through this endpoint.
    """
    email: EmailStr
    name: str
    password: str
    role: UserRole
    company: Optional[str] = None
    avatar_initials: Optional[str] = None
    # Role-specific payload — exactly one of these should be set based on role
    worker_profile: Optional[WorkerProfileCreate] = None
    supervisor_profile: Optional[SupervisorProfileCreate] = None
    team_leader_profile: Optional[TeamLeaderProfileCreate] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class UserUpdate(BaseSchema):
    """Validated input for updating an existing user (owner action).

    Only safe, non-privilege fields can be updated through this endpoint.
    Role changes require careful handling and are gated to owner only.
    """
    name: Optional[str] = None
    company: Optional[str] = None
    avatar_initials: Optional[str] = None
    # Owner can update role, but only through explicit owner action
    role: Optional[UserRole] = None


# ── Output schemas ─────────────────────────────────────────────────────────────


class UserBase(BaseSchema):
    email: EmailStr
    name: str
    role: UserRole
    avatar_initials: str
    company: Optional[str] = None


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


class UserOut(BaseSchema):
    """Safe user representation returned from the management API."""
    id: str
    email: str
    name: str
    role: UserRole
    avatar_initials: str
    company: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # Embedded role profile IDs for quick lookup — avoids a second request
    worker_profile_id: Optional[str] = None
    supervisor_profile_id: Optional[str] = None
    team_leader_profile_id: Optional[str] = None
