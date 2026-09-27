"""
CSRF middleware for cookie-authenticated browser requests.

Only unsafe HTTP methods are protected:

    POST
    PUT
    PATCH
    DELETE

Bearer-token API requests without an authentication cookie are not
subject to CSRF protection because bearer tokens are not automatically
attached by browsers.

Cookie-authenticated requests must provide:

    csrf_token cookie
            +
    X-CSRF-Token header
"""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth.jwt import decode_jwt_token
from app.config import settings
from app.core.csrf import verify_csrf_token


UNSAFE_METHODS = {
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
}


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Protect state-changing cookie-authenticated requests.
    """

    def __init__(self, app):
        super().__init__(app)

        self.exempt_paths = {
            f"{settings.API_V1_STR}/auth/login",
            f"{settings.API_V1_STR}/auth/csrf",
        }

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        if not settings.CSRF_ENABLED:
            return await call_next(request)

        if request.method.upper() not in UNSAFE_METHODS:
            return await call_next(request)

        path = request.url.path

        if path in self.exempt_paths:
            return await call_next(request)

        # No authentication cookie means this request is likely using
        # Authorization: Bearer instead. CSRF does not apply to a token
        # that the browser does not automatically attach.
        access_token = request.cookies.get(
            settings.AUTH_COOKIE_NAME
        )

        if not access_token:
            return await call_next(request)

        payload = decode_jwt_token(
            access_token
        )

        # Let the authentication dependency handle malformed/expired
        # authentication cookies rather than returning a CSRF error first.
        if not payload:
            return await call_next(request)

        user_id = payload.get("sub")

        if not user_id:
            return await call_next(request)

        csrf_cookie = request.cookies.get(
            settings.CSRF_COOKIE_NAME
        )

        csrf_header = request.headers.get(
            settings.CSRF_HEADER_NAME
        )

        if not csrf_cookie or not csrf_header:
            return self._forbidden(
                "CSRF token is required for this request."
            )

        if not hmac_compare(
            csrf_cookie,
            csrf_header,
        ):
            return self._forbidden(
                "Invalid CSRF token."
            )

        if not verify_csrf_token(
            csrf_header,
            str(user_id),
        ):
            return self._forbidden(
                "Invalid CSRF token."
            )

        # Defense in depth:
        # if the browser sends an Origin header, it must be one of the
        # explicitly configured frontend origins.
        origin = request.headers.get("origin")

        if (
            origin
            and settings.BACKEND_CORS_ORIGINS
            and origin not in settings.BACKEND_CORS_ORIGINS
        ):
            return self._forbidden(
                "Request origin is not allowed."
            )

        return await call_next(request)

    @staticmethod
    def _forbidden(
        detail: str,
    ):
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "error": "Forbidden",
                "detail": detail,
            },
        )


def hmac_compare(
    left: str,
    right: str,
) -> bool:
    """
    Constant-time string comparison.

    Used for the cookie/header equality check before the token's
    cryptographic user binding is verified.
    """

    import hmac

    return hmac.compare_digest(
        left.encode("utf-8"),
        right.encode("utf-8"),
    )
