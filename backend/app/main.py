import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.routers import (
    analytics_router,
    auth_router,
    blockers_router,
    dashboard_router,
    notifications_router,
    projects_router,
    report_schedules_router,
    reports_router,
    supervisors_router,
    tasks_router,
    teams_router,
    workers_router,
)
from app.routers.health import router as health_router
from app.core.exceptions import (
    AuthenticationException,
    BusinessRuleException,
    DuplicateEntityException,
    EntityNotFoundException,
    PermissionDeniedException,
    ValidationException,
)

from app.scheduler.scheduler import start as scheduler_start
from app.scheduler.scheduler import shutdown as scheduler_shutdown

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hooks.

    Database schema creation and application-data seeding are intentionally not
    performed here. Alembic owns schema changes, while authenticated/admin
    bootstrap tooling should own initial user creation.

    Development:
    REPORT_SCHEDULER_ENABLED=true may be used with one Uvicorn worker.

    Production:
    Keep REPORT_SCHEDULER_ENABLED=false in API workers.
    Run python -m app.scheduler.worker as one dedicated scheduler process.
    """
    if settings.REPORT_SCHEDULER_ENABLED:
        scheduler_start()

    yield

    if settings.REPORT_SCHEDULER_ENABLED:
        scheduler_shutdown()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── Middleware ─────────────────────────────────────────────────────────────────

# Conditionally enable TrustedHostMiddleware in production.
# Set TRUSTED_HOST_ENABLED=true and TRUSTED_HOSTS=yourdomain.com in production.
# Leave TRUSTED_HOST_ENABLED=false (default) during local development.
if settings.TRUSTED_HOST_ENABLED:
    from starlette.middleware.trustedhost import TrustedHostMiddleware

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.TRUSTED_HOSTS,
    )

from app.middleware.security_headers import SecurityHeadersMiddleware
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


# ── Exception handlers ─────────────────────────────────────────────────────────
# All handlers produce the same flat envelope:
# {"success": false, "error": "<human label>", "detail": "<message>"}
# This preserves frontend compatibility while ensuring no raw exceptions leak.


@app.exception_handler(AuthenticationException)
async def authentication_handler(request: Request, exc: AuthenticationException):
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers or {},
        content={
            "success": False,
            "error": "Unauthorized",
            "detail": exc.detail,
        },
    )


@app.exception_handler(EntityNotFoundException)
async def not_found_handler(request: Request, exc: EntityNotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": "Not Found",
            "detail": exc.detail,
        },
    )


@app.exception_handler(PermissionDeniedException)
async def permission_handler(request: Request, exc: PermissionDeniedException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": "Forbidden",
            "detail": exc.detail,
        },
    )


@app.exception_handler(DuplicateEntityException)
async def duplicate_handler(request: Request, exc: DuplicateEntityException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": "Conflict",
            "detail": exc.detail,
        },
    )


@app.exception_handler(ValidationException)
async def validation_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": "Unprocessable Entity",
            "detail": exc.detail,
        },
    )


@app.exception_handler(BusinessRuleException)
async def business_rule_handler(request: Request, exc: BusinessRuleException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": "Bad Request",
            "detail": exc.detail,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Normalize all remaining raw HTTPExceptions to the flat project envelope.

    This catches exceptions raised directly with HTTPException (e.g. from
    FastAPI internals or third-party dependencies) that are not covered by the
    typed exception handlers above.  It prevents raw {"detail": "..."} responses
    from reaching the client.
    """
    # Map numeric status codes to human-readable labels.
    _STATUS_LABELS: dict[int, str] = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        409: "Conflict",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
        500: "Internal Server Error",
        503: "Service Unavailable",
    }
    label = _STATUS_LABELS.get(exc.status_code, "Error")
    headers = getattr(exc, "headers", None) or {}
    return JSONResponse(
        status_code=exc.status_code,
        headers=headers,
        content={
            "success": False,
            "error": label,
            "detail": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    """Return a consistent 422 shape for Pydantic request validation failures.

    Pydantic v2 errors may contain non-JSON-serializable objects in the 'ctx'
    field (e.g. raw Python exceptions). We sanitize each error dict to ensure
    all values are JSON-safe before returning them to the client.
    """

    def _sanitize_error(err: dict) -> dict:
        """Ensure every value in a Pydantic error dict is JSON-serializable."""
        sanitized: dict = {}
        for key, value in err.items():
            if key == "ctx" and isinstance(value, dict):
                # ctx values may be raw exception instances — stringify them.
                sanitized[key] = {
                    k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                    for k, v in value.items()
                }
            elif not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                sanitized[key] = str(value)
            else:
                sanitized[key] = value
        return sanitized

    safe_errors = [_sanitize_error(e) for e in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Unprocessable Entity",
            "detail": safe_errors,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Global fallback handler for any unhandled Python exception.

    Logs the full traceback for internal investigation.  The client receives a
    generic message — no stack traces, no database URLs, no secret values.
    """
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred.",
        },
    )


# ── Routes ─────────────────────────────────────────────────────────────────────

app.include_router(health_router)
app.include_router(health_router, prefix=settings.API_V1_STR)


app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(projects_router, prefix=settings.API_V1_STR)
app.include_router(workers_router, prefix=settings.API_V1_STR)
app.include_router(supervisors_router, prefix=settings.API_V1_STR)
app.include_router(teams_router, prefix=settings.API_V1_STR)
app.include_router(tasks_router, prefix=settings.API_V1_STR)
app.include_router(blockers_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(report_schedules_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
    }
