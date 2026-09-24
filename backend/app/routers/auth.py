from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    CurrentUserOut,
    UpdateProfileRequest,
    ChangePasswordRequest,
)
from app.services.auth_service import AuthService
from app.services.user_management_service import UserManagementService
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.core.exceptions import AuthenticationException

router = APIRouter(prefix="/auth", tags=["Auth"])


def _build_current_user_out(user: User) -> CurrentUserOut:
    """Map User ORM to CurrentUserOut, including role-profile IDs.

    Profile IDs allow the frontend to directly reference the user's profile
    record without scanning lists by email.
    """
    return CurrentUserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
        company=user.company,
        avatar_initials=user.avatar_initials,
        is_active=user.is_active,
        worker_profile_id=(
            user.worker_profile.id if user.worker_profile else None
        ),
        supervisor_profile_id=(
            user.supervisor_profile.id if user.supervisor_profile else None
        ),
        team_leader_profile_id=(
            user.team_leader_profile.id if user.team_leader_profile else None
        ),
    )


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticate with email and password.

    Sets an HttpOnly cookie with the JWT token and returns it in the payload.
    """
    auth_service = AuthService(db)
    token = auth_service.authenticate_user(login_data)
    if not token:
        raise AuthenticationException("Incorrect email or password.")
        
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        samesite="lax",
        max_age=86400, # 1 day
        secure=False,  # False for dev, should be True for prod (HTTPS)
    )
    return token

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    """Logout the user by clearing the HttpOnly cookie."""
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=CurrentUserOut)
def get_current_user_profile(user: User = Depends(get_current_user)):
    """Return the authenticated user's profile.

    Also includes role-profile IDs so the frontend can identify the user's
    worker/supervisor/team-leader record without searching by email.
    """
    return _build_current_user_out(user)


@router.patch("/me", response_model=CurrentUserOut)
def update_own_profile(
    data: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the authenticated user's own safe profile fields.

    Role and account status cannot be modified through this endpoint.
    Only name, company, and avatar_initials are accepted.
    """
    svc = UserManagementService(db)
    updated_user = svc.update_own_profile(
        user=user,
        name=data.name,
        company=data.company,
        avatar_initials=data.avatar_initials,
    )
    return _build_current_user_out(updated_user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the authenticated user's password.

    Requires the current password for verification.
    The old password will no longer work after this call.
    Existing JWT tokens remain valid until expiry (stateless JWT architecture).
    To force immediate logout of other sessions, the user should log out
    manually from each device.
    """
    svc = UserManagementService(db)
    svc.change_password(
        user=user,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    # 204 No Content — intentionally returns nothing on success
