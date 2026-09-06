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
    from app.routers.projects import get_projects
    from app.models.user import UserRoleEnum

    # OWNER sees all activities
    if _.role == UserRoleEnum.OWNER:
        return (
            db.query(ProjectActivity)
            .order_by(ProjectActivity.timestamp.desc())
            .limit(10)
            .all()
        )

    # For other roles, use the existing project scoping logic
    allowed_projects = get_projects(db=db, current_user=_)
    if not allowed_projects:
        return []
    
    allowed_project_ids = [p.id for p in allowed_projects]

    return (
        db.query(ProjectActivity)
        .filter(ProjectActivity.project_id.in_(allowed_project_ids))
        .order_by(ProjectActivity.timestamp.desc())
        .limit(10)
        .all()
    )
