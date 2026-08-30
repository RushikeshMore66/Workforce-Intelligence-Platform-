import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.blocker import BlockerCreate, BlockerUpdate, BlockerOut
from app.models.blocker import Blocker, BlockerStatusEnum
from app.models.activity import ProjectActivity, ActivityTypeEnum
from app.repositories.blocker_repo import BlockerRepository
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/blockers", tags=["Blockers"])


@router.get("", response_model=List[BlockerOut])
def get_blockers(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    repo = BlockerRepository(db)
    return repo.get_all()


@router.post("", response_model=BlockerOut, status_code=status.HTTP_201_CREATED)
def report_blocker(
    blocker_in: BlockerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
    repo = BlockerRepository(db)
    blocker = repo.get_by_id(blocker_id)
    if not blocker:
        raise EntityNotFoundException("Blocker", blocker_id)

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
