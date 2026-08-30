from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.team import TeamOut
from app.services.team_service import TeamService
from app.repositories.worker_repo import WorkerRepository
from app.schemas.user import WorkerOut
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("", response_model=List[TeamOut])
def get_teams(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = TeamService(db)
    teams = service.get_teams()
    return [
        TeamOut(
            id=t.id,
            name=t.name,
            supervisor_id=t.supervisor_id,
            team_leader_id=t.team_leader_id,
            member_count=len(t.workers) if t.workers else t.member_count,
            project_ids=[p.id for p in t.projects],
        )
        for t in teams
    ]


@router.get("/{team_id}", response_model=TeamOut)
def get_team(
    team_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = TeamService(db)
    t = service.get_team(team_id)
    return TeamOut(
        id=t.id,
        name=t.name,
        supervisor_id=t.supervisor_id,
        team_leader_id=t.team_leader_id,
        member_count=len(t.workers) if t.workers else t.member_count,
        project_ids=[p.id for p in t.projects],
    )


@router.get("/{team_id}/workers", response_model=List[WorkerOut])
def get_team_workers(
    team_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    repo = WorkerRepository(db)
    workers = repo.get_by_team(team_id)
    return [
        WorkerOut(
            id=w.id,
            name=w.user.name if w.user else "Worker",
            email=w.user.email if w.user else "",
            role=w.role,
            team_id=w.team_id,
            team_leader_id=w.team_leader_id,
            supervisor_id=w.supervisor_id,
            avatar_initials=w.user.avatar_initials if w.user else "W",
            status=w.status.value,
            active_project_id=w.active_project_id,
            completed_task_count=w.completed_task_count,
            in_progress_task_count=w.in_progress_task_count,
            pending_task_count=w.pending_task_count,
            blocked_task_count=w.blocked_task_count,
        )
        for w in workers
    ]
