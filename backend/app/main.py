from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import Base, engine, SessionLocal
from app.routers import (
    auth_router,
    projects_router,
    workers_router,
    supervisors_router,
    teams_router,
    tasks_router,
    blockers_router,
    dashboard_router,
    analytics_router,
    notifications_router,
)
from app.core.exceptions import (
    EntityNotFoundException,
    PermissionDeniedException,
    DuplicateEntityException,
    ValidationException,
)
from app.models.user import User, UserRoleEnum
from app.core.security import get_password_hash


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if not existing
    Base.metadata.create_all(bind=engine)

    # Seed default Owner (Rajesh Mehta) if database is empty
    db = SessionLocal()
    try:
        owner = db.query(User).filter(User.email == "rajesh.mehta@apexsoftware.in").first()
        if not owner:
            owner = User(
                id="usr-owner-1",
                name="Rajesh Mehta",
                email="rajesh.mehta@apexsoftware.in",
                hashed_password=get_password_hash("password123"),
                role=UserRoleEnum.OWNER,
                company="Apex Software Solutions",
                avatar_initials="RM",
            )
            db.add(owner)
            db.commit()
    finally:
        db.close()

    yield
    # Shutdown logic if needed


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handlers ──
@app.exception_handler(EntityNotFoundException)
async def not_found_handler(request: Request, exc: EntityNotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": "Not Found", "detail": exc.detail},
    )


@app.exception_handler(PermissionDeniedException)
async def permission_handler(request: Request, exc: PermissionDeniedException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": "Forbidden", "detail": exc.detail},
    )


@app.exception_handler(DuplicateEntityException)
async def duplicate_handler(request: Request, exc: DuplicateEntityException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": "Conflict", "detail": exc.detail},
    )


@app.exception_handler(ValidationException)
async def validation_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": "Unprocessable Entity", "detail": exc.detail},
    )


# ── Health Check ──
@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


# ── Register Routers ──
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


@app.get("/", include_in_schema=False)
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
    }
