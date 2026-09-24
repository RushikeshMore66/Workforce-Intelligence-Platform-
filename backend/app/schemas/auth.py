from typing import Optional
from pydantic import EmailStr, field_validator
from app.schemas.common import BaseSchema, UserRole


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class CurrentUserOut(BaseSchema):
    """Safe representation of the authenticated user — no password hash."""
    id: str
    name: str
    email: str
    role: UserRole
    company: Optional[str] = None
    avatar_initials: str
    is_active: bool
    # Role-specific profile IDs so the frontend can identify profiles without
    # scanning worker/supervisor lists by email.
    worker_profile_id: Optional[str] = None
    supervisor_profile_id: Optional[str] = None
    team_leader_profile_id: Optional[str] = None


class UpdateProfileRequest(BaseSchema):
    """Fields the authenticated user is allowed to update on their own profile.

    Role and is_active are intentionally excluded — those require owner action.
    """
    name: Optional[str] = None
    company: Optional[str] = None
    avatar_initials: Optional[str] = None

    @field_validator("avatar_initials")
    @classmethod
    def validate_initials(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) == 0:
            raise ValueError("avatar_initials cannot be empty")
        return v


class ChangePasswordRequest(BaseSchema):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
