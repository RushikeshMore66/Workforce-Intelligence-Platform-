from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.config import settings
from app.schemas.auth import TokenResponse


def create_jwt_token(
    user_id: str,
    role: str,
    session_version: int = 1,
    expires_delta: Optional[timedelta] = None,
) -> TokenResponse:
    """
    Create an authenticated JWT.

    session_version is stored inside the token so the server can
    invalidate previously issued tokens after sensitive account
    changes such as password changes, role changes, or deactivation.
    """

    now = datetime.utcnow()

    if expires_delta:
        expire = now + expires_delta
        expires_in = int(
            expires_delta.total_seconds()
        )
    else:
        expire = now + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        expires_in = (
            settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    to_encode = {
        "sub": str(user_id),
        "role": str(role),
        "sv": int(session_version),
        "exp": expire,
        "iat": now,
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return TokenResponse(
        access_token=encoded_jwt,
        token_type="bearer",
        expires_in=expires_in,
    )


def decode_jwt_token(
    token: str,
) -> Optional[dict]:
    """
    Decode and cryptographically validate a JWT.

    Returns None when the token is invalid or expired.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        return payload

    except JWTError:
        return None