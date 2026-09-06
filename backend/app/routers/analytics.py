from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.analytics import AnalyticsDataOut
from app.services.analytics_service import AnalyticsService
from app.auth.dependencies import require_supervisor
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsDataOut)
def get_analytics(
    db: Session = Depends(get_db),
    _: User = Depends(require_supervisor),
):
    """Retrieve analytics data. Restricted to OWNER and SUPERVISOR roles."""
    service = AnalyticsService(db)
    return service.get_analytics_data()
