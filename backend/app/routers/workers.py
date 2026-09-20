from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.authorization.policies import (
    _get_supervisor_profile,
    _get_team_leader_profile,
    _get_worker_profile,
    authorize_worker_access,
)
from app.database import get_db
from app.models.task import Task, TaskStatusEnum, WorkUpdate
from app.models.user import User, UserRoleEnum
from app.schemas.analytics import WorkerAnalyticsOut
from app.schemas.common import PaginatedResponse, WorkerStatus
from app.schemas.task import TaskOut, WorkUpdateOut
from app.schemas.user import WorkerOut
from app.services.worker_analytics_service import WorkerAnalyticsService
from app.services.worker_service import WorkerService

router = APIRouter(prefix="/workers", tags=["Workers"])


def _compute_task_counts(worker_id: str, db: Session) -> dict:
    rows = (
        db.query(Task.status, func.count(Task.id))
        .filter(Task.assignee_id == worker_id)
        .group_by(Task.status)
        .all()
    )
    counts = {row[0]: row[1] for row in rows}
    return {
        "completed": counts.get(TaskStatusEnum.COMPLETED, 0),
        "in_progress": counts.get(TaskStatusEnum.IN_PROGRESS, 0),
        "pending": counts.get(TaskStatusEnum.PLANNED, 0),
        "blocked": counts.get(TaskStatusEnum.ON_HOLD, 0),
    }


def _format_worker(worker, db: Session) -> WorkerOut:
    counts = _compute_task_counts(worker.id, db)
    return WorkerOut(
        id=worker.id,
        name=worker.user.name if worker.user else "Unknown",
        email=worker.user.email if worker.user else "",
        role=worker.role,
        team_id=worker.team_id,
        team_leader_id=worker.team_leader_id,
        supervisor_id=worker.supervisor_id,
        avatar_initials=worker.user.avatar_initials if worker.user else "W",
        status=worker.status.value,
        active_project_id=worker.active_project_id,
        completed_task_count=counts["completed"],
        in_progress_task_count=counts["in_progress"],
        pending_task_count=counts["pending"],
        blocked_task_count=counts["blocked"],
    )


@router.get("", response_model=List[WorkerOut])
def get_workers(
    search: Optional[str] = Query(None),
    team_id: Optional[str] = Query(None),
    status: Optional[WorkerStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WorkerService(db)
    all_workers = service.get_workers(search=search, team_id=team_id, status=status)

    if current_user.role == UserRoleEnum.OWNER:
        return [_format_worker(worker, db) for worker in all_workers]

    if current_user.role == UserRoleEnum.SUPERVISOR:
        supervisor = _get_supervisor_profile(current_user, db)
        if not supervisor:
            return []
        allowed_ids = {worker.id for worker in supervisor.workers}
        return [_format_worker(worker, db) for worker in all_workers if worker.id in allowed_ids]

    if current_user.role == UserRoleEnum.TEAM_LEADER:
        leader = _get_team_leader_profile(current_user, db)
        if not leader:
            return []
        allowed_ids = {worker.id for worker in leader.workers}
        return [_format_worker(worker, db) for worker in all_workers if worker.id in allowed_ids]

    if current_user.role == UserRoleEnum.WORKER:
        own_worker = _get_worker_profile(current_user, db)
        if not own_worker:
            return []
        return [_format_worker(worker, db) for worker in all_workers if worker.id == own_worker.id]

    return []


@router.get("/{worker_id}", response_model=WorkerOut)
def get_worker(
    worker_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    worker = authorize_worker_access(worker_id, current_user, db)
    return _format_worker(worker, db)


@router.get("/{worker_id}/tasks", response_model=PaginatedResponse[TaskOut])
def get_worker_tasks(
    worker_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    authorize_worker_access(worker_id, current_user, db)
    query = db.query(Task).filter(Task.assignee_id == worker_id)
    total = query.count()
    items = (
        query.order_by(Task.due_date.asc(), Task.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(items=items, page=page, page_size=page_size, total=total)


@router.get("/{worker_id}/updates", response_model=PaginatedResponse[WorkUpdateOut])
def get_worker_updates(
    worker_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    authorize_worker_access(worker_id, current_user, db)
    query = db.query(WorkUpdate).filter(WorkUpdate.worker_id == worker_id)
    total = query.count()
    items = (
        query.order_by(WorkUpdate.timestamp.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(items=items, page=page, page_size=page_size, total=total)


@router.get("/{worker_id}/analytics", response_model=WorkerAnalyticsOut)
def get_worker_analytics_data(
    worker_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    authorize_worker_access(worker_id, current_user, db)
    return WorkerAnalyticsService(db).get_worker_analytics(worker_id)
