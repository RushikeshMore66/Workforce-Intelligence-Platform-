from datetime import datetime
from typing import Optional

from pydantic import EmailStr, field_validator

from app.schemas.common import BaseSchema, UserRole


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


class LoginResponse(BaseSchema):
    """
    Browser login response.

    The JWT is delivered only through the HttpOnly authentication cookie.
    It is intentionally not returned in the JSON response.
    """

    authenticated: bool
    expires_in: int


class TokenResponse(BaseSchema):
    """
    Internal/legacy token representation.

    The browser login endpoint must not expose access_token.
    """

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class CurrentUserOut(BaseSchema):
    """Safe representation of the authenticated user."""

    id: str
    name: str
    email: str
    role: UserRole
    company: Optional[str] = None
    avatar_initials: str
    is_active: bool

    worker_profile_id: Optional[str] = None
    supervisor_profile_id: Optional[str] = None
    team_leader_profile_id: Optional[str] = None


class UpdateProfileRequest(BaseSchema):
    """
    Fields the authenticated user may modify.
    """

    name: Optional[str] = None
    company: Optional[str] = None
    avatar_initials: Optional[str] = None

    @field_validator("avatar_initials")
    @classmethod
    def validate_initials(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError(
                "avatar_initials cannot be empty"
            )

        return value


class ChangePasswordRequest(BaseSchema):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(
        cls,
        value: str,
    ) -> str:
        if len(value) < 8:
            raise ValueError(
                "Password must be at least 8 characters long"
            )

        return value