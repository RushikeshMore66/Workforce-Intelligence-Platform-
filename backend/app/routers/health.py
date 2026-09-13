from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import settings
from app.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])

@router.get("/health/live", summary="Liveness Probe")
def liveness():
    """Returns 200 OK immediately. Used by load balancers and orchestrators
    to check if the API process is alive and accepting connections.
    """
    return {"status": "ok"}

@router.get("/health/ready", summary="Readiness Probe")
def readiness(db: Session = Depends(get_db)):
    """Checks required dependencies (like the database).
    Returns 200 OK if ready, 503 if degraded.
    """
    health_status = {"status": "ready", "database": "ok"}
    http_status = status.HTTP_200_OK

    try:
        # Fast query to ensure DB is responsive
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("Readiness probe database check failed: %s", e)
        health_status["status"] = "degraded"
        health_status["database"] = "error"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(status_code=http_status, content=health_status)

# Keep the legacy endpoints exactly as they are for existing clients
@router.get("/health", summary="Legacy Health Check")
def legacy_health_check():
    """Legacy health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }
