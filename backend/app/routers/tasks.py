import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, WorkUpdateCreate, WorkUpdateOut
from app.models.task import Task, WorkUpdate, TaskTransition
from app.models.activity import ProjectActivity, ActivityTypeEnum
from app.models.user import User, UserRoleEnum
from app.repositories.task_repo import TaskRepository
from app.auth.dependencies import (
    get_current_user,
    require_team_lead,
    authorize_task_access,
    _get_worker_profile,
)
from app.core.exceptions import EntityNotFoundException, PermissionDeniedException

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a task. Raises 403 if the user is not authorized to see it."""
    return authorize_task_access(task_id, current_user, db)


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_team_lead),
):
    """Create a task. Requires OWNER, SUPERVISOR, or TEAM_LEADER role."""
    repo = TaskRepository(db)
    task_dict = task_in.model_dump()
    task_dict["id"] = f"task-{uuid.uuid4().hex[:6]}"
    task = repo.create(task_dict)
    return task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a task. Workers may only update their own assigned tasks."""
    # Read the task to perform authorization checks
    authorize_task_access(task_id, current_user, db)

    update_data = task_in.model_dump(exclude_unset=True)

    # Lock the task row exclusively if status might be changing to prevent transition history races
    if "status" in update_data:
        task = db.query(Task).with_for_update().filter(Task.id == task_id).first()
    else:
        task = db.query(Task).filter(Task.id == task_id).first()

    old_status = task.status
    new_status = update_data.get("status")

    transition = None
    if new_status and new_status != old_status:
        transition = TaskTransition(
            id=f"tt-{uuid.uuid4().hex[:6]}",
            task_id=task.id,
            from_status=old_status,
            to_status=new_status,
            changed_by_user_id=current_user.id
        )

    # Apply changes
    for field, value in update_data.items():
        setattr(task, field, value)
        
    db.add(task)
    if transition:
        db.add(transition)

    # Log task activity
    activity = ProjectActivity(
        id=f"act-{uuid.uuid4().hex[:6]}",
        project_id=task.project_id,
        description=f"Task '{task.title}' updated by {current_user.name}.",
        user_id=current_user.id,
        user_name=current_user.name,
        type=ActivityTypeEnum.TASK_UPDATED,
    )
    if new_status and new_status != old_status:
        if new_status == "COMPLETED":
            activity.type = ActivityTypeEnum.TASK_COMPLETED
        else:
            activity.type = ActivityTypeEnum.TASK_STATUS_CHANGED

    db.add(activity)
    db.commit()
    db.refresh(task)

    return task


@router.post("/{task_id}/updates", response_model=WorkUpdateOut, status_code=status.HTTP_201_CREATED)
def add_work_update(
    task_id: str,
    update_in: WorkUpdateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a work update to a task.

    Workers may only post updates on their own assigned tasks.
    Supervisors and Team Leaders may post on tasks within their scope.
    """
    from fastapi import HTTPException
    task = authorize_task_access(task_id, current_user, db)

    if not task.assignee_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot post update to an unassigned task")

    work_update = WorkUpdate(
        id=f"wu-{uuid.uuid4().hex[:6]}",
        task_id=task_id,
        worker_id=task.assignee_id,
        created_by_user_id=current_user.id,
        description=update_in.description,
    )
    db.add(work_update)
    db.commit()
    db.refresh(work_update)
    return work_update
