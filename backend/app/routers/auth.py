from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, CurrentUserOut
from app.services.auth_service import AuthService
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    token = auth_service.authenticate_user(login_data)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    return token


@router.get("/me", response_model=CurrentUserOut)
def get_current_user_profile(user: User = Depends(get_current_user)):
    return CurrentUserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
        company=user.company,
        avatar_initials=user.avatar_initials,
    )
