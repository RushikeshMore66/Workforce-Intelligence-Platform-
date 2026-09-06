import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.blocker import BlockerCreate, BlockerUpdate, BlockerOut
from app.models.blocker import Blocker, BlockerStatusEnum
from app.models.activity import ProjectActivity, ActivityTypeEnum
from app.models.user import User, UserRoleEnum
from app.repositories.blocker_repo import BlockerRepository
from app.auth.dependencies import (
    get_current_user,
    authorize_project_access,
    authorize_blocker_access,
    _get_supervisor_profile,
    _get_team_leader_profile,
    _get_worker_profile,
)
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/blockers", tags=["Blockers"])


@router.get("", response_model=List[BlockerOut])
def get_blockers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List blockers scoped to the user's accessible projects.

    OWNER      → all blockers.
    SUPERVISOR → blockers from their assigned projects.
    TEAM_LEADER→ blockers from their team's projects.
    WORKER     → blockers from their team's projects.
    """
    repo = BlockerRepository(db)
    all_blockers = repo.get_all()

    if current_user.role == UserRoleEnum.OWNER:
        return all_blockers

    if current_user.role == UserRoleEnum.SUPERVISOR:
        sup = _get_supervisor_profile(current_user, db)
        if not sup:
            return []
        allowed_project_ids = {p.id for p in sup.projects}
        return [b for b in all_blockers if b.project_id in allowed_project_ids]

    if current_user.role == UserRoleEnum.TEAM_LEADER:
        leader = _get_team_leader_profile(current_user, db)
        if not leader or not leader.team:
            return []
        allowed_project_ids = {p.id for p in leader.team.projects}
        return [b for b in all_blockers if b.project_id in allowed_project_ids]

    if current_user.role == UserRoleEnum.WORKER:
        worker = _get_worker_profile(current_user, db)
        if not worker or not worker.team:
            return []
        allowed_project_ids = {p.id for p in worker.team.projects}
        return [b for b in all_blockers if b.project_id in allowed_project_ids]

    return []


@router.post("", response_model=BlockerOut, status_code=status.HTTP_201_CREATED)
def report_blocker(
    blocker_in: BlockerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Report a blocker. User must have access to the referenced project."""
    # Verify user can access the project before allowing a blocker to be reported
    authorize_project_access(blocker_in.project_id, current_user, db)

    repo = BlockerRepository(db)
    blocker_dict = blocker_in.model_dump()
    blocker_dict["id"] = f"blk-{uuid.uuid4().hex[:6]}"
    blocker_dict["reported_by_id"] = current_user.id
    blocker_dict["status"] = BlockerStatusEnum.OPEN
    blocker_dict["created_date"] = datetime.utcnow().date()

    blocker = repo.create(blocker_dict)

    # Activity log
    activity = ProjectActivity(
        id=f"act-{uuid.uuid4().hex[:6]}",
        project_id=blocker.project_id,
        description=f"Blocker reported: '{blocker.title}' by {current_user.name}.",
        user_id=current_user.id,
        user_name=current_user.name,
        type=ActivityTypeEnum.BLOCKER_REPORTED,
    )
    db.add(activity)
    db.commit()

    return blocker


@router.patch("/{blocker_id}", response_model=BlockerOut)
def update_blocker(
    blocker_id: str,
    blocker_in: BlockerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a blocker. User must have access to the blocker's parent project."""
    blocker = authorize_blocker_access(blocker_id, current_user, db)

    repo = BlockerRepository(db)
    updated_data = blocker_in.model_dump(exclude_unset=True)
    if blocker_in.status == BlockerStatusEnum.RESOLVED and not blocker.resolved_date:
        updated_data["resolved_date"] = datetime.utcnow().date()
        # Activity log
        activity = ProjectActivity(
            id=f"act-{uuid.uuid4().hex[:6]}",
            project_id=blocker.project_id,
            description=f"Blocker resolved: '{blocker.title}' by {current_user.name}.",
            user_id=current_user.id,
            user_name=current_user.name,
            type=ActivityTypeEnum.BLOCKER_RESOLVED,
        )
        db.add(activity)

    updated = repo.update(blocker, updated_data)
    return updated
