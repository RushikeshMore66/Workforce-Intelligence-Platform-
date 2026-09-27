from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.jwt import decode_jwt_token
from app.config import settings
from app.core.csrf import create_csrf_token
from app.core.exceptions import AuthenticationException
from app.core.rate_limiter import LoginRateLimiter
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    CurrentUserOut,
    LoginRequest,
    LoginResponse,
    UpdateProfileRequest,
)
from app.services.auth_service import AuthService
from app.services.user_management_service import UserManagementService


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


login_rate_limiter = LoginRateLimiter(
    maximum_attempts=settings.RATE_LIMIT_LOGIN_ATTEMPTS,
    window_seconds=settings.RATE_LIMIT_LOGIN_WINDOW_SECONDS,
)


def _build_current_user_out(
    user: User,
) -> CurrentUserOut:
    return CurrentUserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
        company=user.company,
        avatar_initials=user.avatar_initials,
        is_active=user.is_active,
        worker_profile_id=(
            user.worker_profile.id
            if user.worker_profile
            else None
        ),
        supervisor_profile_id=(
            user.supervisor_profile.id
            if user.supervisor_profile
            else None
        ),
        team_leader_profile_id=(
            user.team_leader_profile.id
            if user.team_leader_profile
            else None
        ),
    )


def _get_client_key(
    request,
) -> str:
    """
    Use the directly observed client address.

    We intentionally do not trust X-Forwarded-For here.
    A production reverse proxy should enforce its own trusted
    client-IP handling before passing requests downstream.
    """

    if request.client is None:
        return "unknown"

    return request.client.host


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    login_data: LoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Browser login.

    Successful authentication creates:

        access_token cookie
        csrf_token cookie

    The JWT is never returned in JSON.
    """

    rate_key = _get_client_key(
        request
    )

    if settings.RATE_LIMIT_ENABLED:
        allowed, retry_after = (
            login_rate_limiter.allow(
                rate_key
            )
        )

        if not allowed:
            response.headers["Retry-After"] = str(
                retry_after
            )

            from fastapi import HTTPException

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    "Too many login attempts. "
                    f"Try again in {retry_after} seconds."
                ),
                headers={
                    "Retry-After": str(
                        retry_after
                    )
                },
            )

    auth_service = AuthService(db)

    token = auth_service.authenticate_user(
        login_data
    )

    if not token:
        if settings.RATE_LIMIT_ENABLED:
            login_rate_limiter.record_failure(
                rate_key
            )

        raise AuthenticationException(
            "Incorrect email or password."
        )

    if settings.RATE_LIMIT_ENABLED:
        login_rate_limiter.reset(
            rate_key
        )

    payload = decode_jwt_token(
        token.access_token
    )

    if payload is None or not payload.get("sub"):
        raise AuthenticationException(
            "Unable to establish authentication session."
        )

    user_id = str(
        payload["sub"]
    )

    csrf_token = create_csrf_token(
        user_id
    )

    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token.access_token,
        httponly=True,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=token.expires_in,
        secure=settings.AUTH_COOKIE_SECURE,
        path=settings.AUTH_COOKIE_PATH,
    )

    response.set_cookie(
        key=settings.CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=False,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=token.expires_in,
        secure=settings.AUTH_COOKIE_SECURE,
        path=settings.CSRF_COOKIE_PATH,
    )

    return LoginResponse(
        authenticated=True,
        expires_in=token.expires_in,
    )


@router.get(
    "/csrf",
)
def get_csrf_token(
    response: Response,
    user: User = Depends(get_current_user),
):
    """
    Refresh/create the browser CSRF cookie for an authenticated user.

    The token is deliberately returned only through the cookie.
    JavaScript reads it from document.cookie.
    """

    csrf_token = create_csrf_token(
        user.id
    )

    response.set_cookie(
        key=settings.CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=False,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=settings.AUTH_COOKIE_SECURE,
        path=settings.CSRF_COOKIE_PATH,
    )

    return {
        "csrf_enabled": settings.CSRF_ENABLED
    }


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    response: Response,
):
    response.delete_cookie(
        key=settings.AUTH_COOKIE_NAME,
        httponly=True,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        secure=settings.AUTH_COOKIE_SECURE,
        path=settings.AUTH_COOKIE_PATH,
    )

    response.delete_cookie(
        key=settings.CSRF_COOKIE_NAME,
        httponly=False,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        secure=settings.AUTH_COOKIE_SECURE,
        path=settings.CSRF_COOKIE_PATH,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.get(
    "/me",
    response_model=CurrentUserOut,
)
def get_current_user_profile(
    user: User = Depends(get_current_user),
):
    return _build_current_user_out(
        user
    )


@router.patch(
    "/me",
    response_model=CurrentUserOut,
)
def update_own_profile(
    data: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = UserManagementService(db)

    updated_user = service.update_own_profile(
        user=user,
        name=data.name,
        company=data.company,
        avatar_initials=data.avatar_initials,
    )

    return _build_current_user_out(
        updated_user
    )


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = UserManagementService(db)

    service.change_password(
        user=user,
        current_password=data.current_password,
        new_password=data.new_password,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
