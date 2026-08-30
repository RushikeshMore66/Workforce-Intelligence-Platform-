from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_password, get_password_hash
from app.auth.jwt import create_jwt_token
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, login_data: LoginRequest) -> Optional[TokenResponse]:
        user = self.db.query(User).filter(User.email == login_data.email).first()
        if not user:
            return None
        if not verify_password(login_data.password, user.hashed_password):
            return None
        return create_jwt_token(user_id=user.id, role=user.role.value)
