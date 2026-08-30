from typing import Optional
from pydantic import EmailStr
from app.schemas.common import BaseSchema, UserRole


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class CurrentUserOut(BaseSchema):
    id: str
    name: str
    email: str
    role: UserRole
    company: Optional[str] = None
    avatar_initials: str
