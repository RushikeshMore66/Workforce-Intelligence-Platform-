import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.authorization.dependencies import RequirePermission
from app.authorization.permissions import Permission
from app.authorization.policies import authorize_project_access, authorize_task_access
from app.core.exceptions import PermissionDeniedException
from app.database import get_db
from app.models.activity import ActivityTypeEnum, ProjectActivity
from app.models.task import Task, WorkUpdate
from app.models.user import User, UserRoleEnum
from app.repositories.task_repo import TaskRepository
from app.schemas.task import (
    TaskCreate,
    TaskOut,
    TaskStatusChange,
    TaskUpdate,
    WorkUpdateCreate,
    WorkUpdateOut,
)
from app.services.project_progress_service import ProjectProgressService
from app.services.task_workflow_service import TaskWorkflowService

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
    current_user: User = Depends(RequirePermission(Permission.TASK_CREATE)),
):
    """Create a task. Requires OWNER, SUPERVISOR, or TEAM_LEADER role.

    The task's project must be accessible to the current user.
    New tasks always start in PLANNED status.
    """
    authorize_project_access(task_in.project_id, current_user, db)

    task_dict = task_in.model_dump()
    task_dict["id"] = f"task-{uuid.uuid4().hex[:6]}"
    task = Task(**task_dict)

    activity = ProjectActivity(
        id=f"act-task-created-{uuid.uuid4().hex[:10]}",
        project_id=task.project_id,
        description=f"Task '{task.title}' was created by {current_user.name}.",
        user_id=current_user.id,
        user_name=current_user.name,
        type=ActivityTypeEnum.TASK_CREATED,
    )

    db.add(task)
    db.add(activity)
    ProjectProgressService.recalculate_project_progress(db, task.project_id)
    db.commit()
    db.refresh(task)

    return task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update task metadata (title, description, assignee, priority, due_date).

    Workers cannot use this endpoint — their operational action is the
    dedicated status-transition endpoint and work updates.
    To change task status use POST /{task_id}/status.
    """
    task = authorize_task_access(task_id, current_user, db)

    if current_user.role == UserRoleEnum.WORKER:
        raise PermissionDeniedException(
            "Workers can only update their work status and submit work updates."
        )

    update_data = task_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    activity = ProjectActivity(
        id=f"act-{uuid.uuid4().hex[:6]}",
        project_id=task.project_id,
        description=f"Task '{task.title}' metadata updated by {current_user.name}.",
        user_id=current_user.id,
        user_name=current_user.name,
        type=ActivityTypeEnum.TASK_UPDATED,
    )

    db.add(task)
    db.add(activity)
    db.commit()
    db.refresh(task)

    return task


@router.post("/{task_id}/status", response_model=TaskOut)
def change_task_status(
    task_id: str,
    status_in: TaskStatusChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change task status through the workflow engine.

    Validates the transition against the canonical state machine:
      PLANNED → IN_PROGRESS | CANCELLED
      IN_PROGRESS → ON_HOLD | COMPLETED | CANCELLED
      ON_HOLD → IN_PROGRESS | CANCELLED

    Workers may only transition their own assigned tasks through legal paths.
    Workers cannot cancel tasks.
    ON_HOLD requires a non-empty reason.
    """
    return TaskWorkflowService(db).transition(
        task_id=task_id,
        to_status=status_in.status,
        current_user=current_user,
        reason=status_in.reason,
    )


@router.post(
    "/{task_id}/updates",
    response_model=WorkUpdateOut,
    status_code=status.HTTP_201_CREATED,
)
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
    task = authorize_task_access(task_id, current_user, db)

    if not task.assignee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot post an update to an unassigned task.",
        )

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

