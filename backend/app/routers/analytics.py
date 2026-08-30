from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.analytics import AnalyticsDataOut
from app.services.analytics_service import AnalyticsService
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsDataOut)
def get_analytics(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    return service.get_analytics_data()
