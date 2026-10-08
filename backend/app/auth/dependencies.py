from typing import List, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.jwt import decode_jwt_token
from app.models.user import User, UserRoleEnum, Supervisor, TeamLeader, Worker
from app.models.project import Project
from app.models.blocker import Blocker
from app.models.notification import Notification
from app.core.exceptions import PermissionDeniedException, EntityNotFoundException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate JWT and return the authenticated User from the database.

    Raises HTTP 401 if the token is missing, invalid, expired, or the account
    is deactivated.  The user identity is always resolved from the database —
    never trusted from the token claims alone.  Account status is re-checked on
    every request so deactivation takes effect immediately without waiting for
    token expiry.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try to extract from Authorization header, fallback to cookie
    token = token or request.cookies.get("access_token")
    
    if not token:
        raise credentials_exception

    payload = decode_jwt_token(token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    # Session revocation check — verify that the token's session version matches
    # the user's current session_version in the database. Tokens issued prior to
    # password change or account deactivation/reactivation are rejected immediately.
    token_sv = payload.get("sv")
    if token_sv is None:
        token_sv = payload.get("session_version")
    user_sv = getattr(user, "session_version", 1) or 1
    if token_sv is not None:
        if int(token_sv) != user_sv:
            raise credentials_exception
    else:
        if user_sv > 1:
            raise credentials_exception

    # Account lifecycle check — deactivated users must not be able to continue
    # using a previously issued token.  This is checked on every request so that
    # deactivation takes effect without waiting for token expiry.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account has been deactivated. Contact your organisation owner.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
