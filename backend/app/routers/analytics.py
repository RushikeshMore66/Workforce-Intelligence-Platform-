from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.analytics import AnalyticsDataOut, OrganizationAnalyticsOut
from app.services.analytics_service import AnalyticsService
from app.services.organization_analytics_service import OrganizationAnalyticsService
from app.authorization.dependencies import RequirePermission
from app.authorization.permissions import Permission
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsDataOut)
def get_analytics(
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission(Permission.ORGANIZATION_VIEW)),
):
    """Retrieve analytics data. Restricted to OWNER and SUPERVISOR roles."""
    service = AnalyticsService(db)
    return service.get_analytics_data()


@router.get("/organization", response_model=OrganizationAnalyticsOut)
def get_organization_analytics(
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission(Permission.ORGANIZATION_UPDATE)),
):
    """Retrieve organization-level analytics data. Restricted to OWNER role."""
    service = OrganizationAnalyticsService(db)
    return service.get_organization_analytics()
