from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import WorkerOut
from app.schemas.common import WorkerStatus, PaginatedResponse
from app.schemas.task import TaskOut, WorkUpdateOut
from app.schemas.analytics import WorkerAnalyticsOut
from app.services.worker_service import WorkerService
from app.services.worker_analytics_service import WorkerAnalyticsService
from app.models.user import User, UserRoleEnum
from app.models.task import Task, WorkUpdate
from app.auth.dependencies import (
    get_current_user,
    authorize_worker_access,
    _get_supervisor_profile,
    _get_team_leader_profile,
    _get_worker_profile,
)

router = APIRouter(prefix="/workers", tags=["Workers"])


def _format_worker(w) -> WorkerOut:
    return WorkerOut(
        id=w.id,
        name=w.user.name if w.user else "Unknown",
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


@router.get("", response_model=List[WorkerOut])
def get_workers(
    search: Optional[str] = Query(None),
    team_id: Optional[str] = Query(None),
    status: Optional[WorkerStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List workers scoped to the authenticated user's authorization level.

    OWNER      → all workers.
    SUPERVISOR → workers in their assigned teams.
    TEAM_LEADER→ workers in their own team.
    WORKER     → only themselves.
    """
    service = WorkerService(db)
    all_workers = service.get_workers(search=search, team_id=team_id, status=status)

    if current_user.role == UserRoleEnum.OWNER:
        return [_format_worker(w) for w in all_workers]

    if current_user.role == UserRoleEnum.SUPERVISOR:
        sup = _get_supervisor_profile(current_user, db)
        if not sup:
            return []
        allowed_ids = {w.id for w in sup.workers}
        return [_format_worker(w) for w in all_workers if w.id in allowed_ids]

    if current_user.role == UserRoleEnum.TEAM_LEADER:
        leader = _get_team_leader_profile(current_user, db)
        if not leader:
            return []
        allowed_ids = {w.id for w in leader.workers}
        return [_format_worker(w) for w in all_workers if w.id in allowed_ids]

    if current_user.role == UserRoleEnum.WORKER:
        own_worker = _get_worker_profile(current_user, db)
        if not own_worker:
            return []
        return [_format_worker(w) for w in all_workers if w.id == own_worker.id]

    return []


@router.get("/{worker_id}", response_model=WorkerOut)
def get_worker(
    worker_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a single worker. Raises 403 if the user cannot access it."""
    w = authorize_worker_access(worker_id, current_user, db)
    return _format_worker(w)


@router.get("/{worker_id}/tasks", response_model=PaginatedResponse[TaskOut])
def get_worker_tasks(
    worker_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tasks assigned to a specific worker."""
    authorize_worker_access(worker_id, current_user, db)
    
    query = db.query(Task).filter(Task.assignee_id == worker_id)
    total = query.count()
    items = query.order_by(Task.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )


@router.get("/{worker_id}/updates", response_model=PaginatedResponse[WorkUpdateOut])
def get_worker_updates(
    worker_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get work updates belonging to a specific worker."""
    authorize_worker_access(worker_id, current_user, db)
    
    query = db.query(WorkUpdate).filter(WorkUpdate.worker_id == worker_id)
    total = query.count()
    items = query.order_by(WorkUpdate.timestamp.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )


@router.get("/{worker_id}/analytics", response_model=WorkerAnalyticsOut)
def get_worker_analytics_data(
    worker_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get deterministic analytics data for a specific worker."""
    authorize_worker_access(worker_id, current_user, db)
    
    service = WorkerAnalyticsService(db)
    return service.get_worker_analytics(worker_id)
