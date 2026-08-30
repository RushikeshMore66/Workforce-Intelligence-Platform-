from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import WorkerOut
from app.schemas.common import WorkerStatus
from app.services.worker_service import WorkerService
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/workers", tags=["Workers"])


@router.get("", response_model=List[WorkerOut])
def get_workers(
    search: Optional[str] = Query(None),
    team_id: Optional[str] = Query(None),
    status: Optional[WorkerStatus] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = WorkerService(db)
    workers = service.get_workers(search=search, team_id=team_id, status=status)
    return [
        WorkerOut(
            id=w.id,
            name=w.user.name if w.user else "Unknown",
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


@router.get("/{worker_id}", response_model=WorkerOut)
def get_worker(
    worker_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = WorkerService(db)
    w = service.get_worker(worker_id)
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
        active_project_id=w.active_project_id,
        completed_task_count=w.completed_task_count,
        in_progress_task_count=w.in_progress_task_count,
        pending_task_count=w.pending_task_count,
        blocked_task_count=w.blocked_task_count,
    )
