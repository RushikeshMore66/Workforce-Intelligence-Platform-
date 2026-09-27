"""
CSRF protection utilities.

The application uses HttpOnly JWT cookies for browser authentication.
Because browsers automatically attach cookies, state-changing requests
need an additional proof that the request originated from our frontend.

We use a signed double-submit cookie pattern:

    csrf_token cookie
            +
    X-CSRF-Token header
            ↓
        HMAC verification

The token is cryptographically bound to the authenticated user ID.

The CSRF cookie itself is intentionally NOT HttpOnly because the frontend
must read it and send it through a custom request header.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

from app.config import settings


def create_csrf_token(user_id: str) -> str:
    """
    Create a signed CSRF token bound to a specific user.

    Token format:

        nonce.signature

    The nonce is random and the signature is an HMAC over:

        user_id:nonce
    """

    nonce = secrets.token_urlsafe(32)

    message = f"{user_id}:{nonce}".encode("utf-8")

    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()

    return f"{nonce}.{signature}"


def verify_csrf_token(
    token: str,
    user_id: str,
) -> bool:
    """
    Verify that the supplied CSRF token was signed by the server
    and belongs to the authenticated user.
    """

    if not token:
        return False

    try:
        nonce, signature = token.split(".", 1)
    except ValueError:
        return False

    if not nonce or not signature:
        return False

    message = f"{user_id}:{nonce}".encode("utf-8")

    expected_signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        signature,
        expected_signature,
    )
