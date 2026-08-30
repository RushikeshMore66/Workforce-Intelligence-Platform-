from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.dashboard import DashboardMetricsOut, AttentionItemOut
from app.schemas.activity import ActivityOut
from app.services.dashboard_service import DashboardService
from app.models.activity import ProjectActivity
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=DashboardMetricsOut)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = DashboardService(db)
    return service.get_metrics()


@router.get("/attention", response_model=List[AttentionItemOut])
def get_attention_items(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = DashboardService(db)
    return service.get_attention_items()


@router.get("/activities", response_model=List[ActivityOut])
def get_recent_activities(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return (
        db.query(ProjectActivity)
        .order_by(ProjectActivity.timestamp.desc())
        .limit(10)
        .all()
    )
