from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.team import TeamOut
from app.services.team_service import TeamService
from app.repositories.worker_repo import WorkerRepository
from app.schemas.user import WorkerOut
from app.models.user import User, UserRoleEnum
from app.auth.dependencies import (
    get_current_user,
    authorize_team_access,
    _get_supervisor_profile,
    _get_team_leader_profile,
    _get_worker_profile,
)
from app.schemas.analytics import TeamAnalyticsOut
from app.services.team_analytics_service import TeamAnalyticsService
from app.core.exceptions import EntityNotFoundException, PermissionDeniedException

router = APIRouter(prefix="/teams", tags=["Teams"])


def _format_team(t) -> TeamOut:
    return TeamOut(
        id=t.id,
        name=t.name,
        supervisor_id=t.supervisor_id,
        team_leader_id=t.leader.id if t.leader else None,
        member_count=len(t.workers) if t.workers else 0,
        project_ids=[p.id for p in t.projects],
    )


def _format_worker(w) -> WorkerOut:
    return WorkerOut(
        id=w.id,
        name=w.user.name if w.user else "Worker",
        email=w.user.email if w.user else "",
        role=w.role,
        team_id=w.team_id,
        team_leader_id=w.team_leader_id,
        supervisor_id=w.supervisor_id,
        avatar_initials=w.user.avatar_initials if w.user else "W",
        status=w.status.value,
        active_project_id=getattr(w, "active_project_id", None),
        completed_task_count=getattr(w, "completed_task_count", 0),
        in_progress_task_count=getattr(w, "in_progress_task_count", 0),
        pending_task_count=getattr(w, "pending_task_count", 0),
        blocked_task_count=getattr(w, "blocked_task_count", 0),
    )


@router.get("", response_model=List[TeamOut])
def get_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List teams scoped to the authenticated user's authorization level.

    OWNER      → all teams.
    SUPERVISOR → only their assigned teams.
    TEAM_LEADER→ only their own team.
    WORKER     → only their own team.
    """
    service = TeamService(db)
    all_teams = service.get_teams()

    if current_user.role == UserRoleEnum.OWNER:
        return [_format_team(t) for t in all_teams]

    if current_user.role == UserRoleEnum.SUPERVISOR:
        sup = _get_supervisor_profile(current_user, db)
        if not sup:
            return []
        allowed_ids = {t.id for t in sup.teams}
        return [_format_team(t) for t in all_teams if t.id in allowed_ids]

    if current_user.role == UserRoleEnum.TEAM_LEADER:
        leader = _get_team_leader_profile(current_user, db)
        if not leader or not leader.team_id:
            return []
        return [_format_team(t) for t in all_teams if t.id == leader.team_id]

    if current_user.role == UserRoleEnum.WORKER:
        worker = _get_worker_profile(current_user, db)
        if not worker or not worker.team_id:
            return []
        return [_format_team(t) for t in all_teams if t.id == worker.team_id]

    return []


@router.get("/{team_id}", response_model=TeamOut)
def get_team(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a single team. Raises 403 if the user is not authorized to see it."""
    t = authorize_team_access(team_id, current_user, db)
    return _format_team(t)


@router.get("/{team_id}/workers", response_model=List[WorkerOut])
def get_team_workers(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List workers in a team. User must be authorized to see the team."""
    authorize_team_access(team_id, current_user, db)

    repo = WorkerRepository(db)
    workers = repo.get_by_team(team_id)
    return [_format_worker(w) for w in workers]


@router.get("/{team_id}/analytics", response_model=TeamAnalyticsOut)
def get_team_analytics_data(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get deterministic analytics data for a specific team."""
    authorize_team_access(team_id, current_user, db)
    
    service = TeamAnalyticsService(db)
    return service.get_team_analytics(team_id)
