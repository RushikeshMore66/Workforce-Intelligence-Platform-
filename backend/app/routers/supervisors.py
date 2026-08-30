from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import SupervisorOut
from app.services.supervisor_service import SupervisorService
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/supervisors", tags=["Supervisors"])


@router.get("", response_model=List[SupervisorOut])
def get_supervisors(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = SupervisorService(db)
    sups = service.get_supervisors()
    return [
        SupervisorOut(
            id=s.id,
            user_id=s.user_id,
            name=s.user.name if s.user else "Supervisor",
            email=s.user.email if s.user else "",
            avatar_initials=s.user.avatar_initials if s.user else "S",
            project_ids=[p.id for p in s.projects],
            team_ids=[t.id for t in s.teams],
        )
        for s in sups
    ]


@router.get("/{supervisor_id}", response_model=SupervisorOut)
def get_supervisor(
    supervisor_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = SupervisorService(db)
    s = service.get_supervisor(supervisor_id)
    return SupervisorOut(
        id=s.id,
        user_id=s.user_id,
        name=s.user.name if s.user else "Supervisor",
        email=s.user.email if s.user else "",
        avatar_initials=s.user.avatar_initials if s.user else "S",
        project_ids=[p.id for p in s.projects],
        team_ids=[t.id for t in s.teams],
    )
