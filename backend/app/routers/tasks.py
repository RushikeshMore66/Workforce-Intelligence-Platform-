import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, WorkUpdateCreate, WorkUpdateOut
from app.models.task import Task, WorkUpdate
from app.models.activity import ProjectActivity, ActivityTypeEnum
from app.repositories.task_repo import TaskRepository
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    if not task:
        raise EntityNotFoundException("Task", task_id)
    return task


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    if not task:
        raise EntityNotFoundException("Task", task_id)
    
    updated = repo.update(task, task_in.model_dump(exclude_unset=True))
    
    # Log task activity
    activity = ProjectActivity(
        id=f"act-{uuid.uuid4().hex[:6]}",
        project_id=task.project_id,
        description=f"Task '{task.title}' updated by {current_user.name}.",
        user_id=current_user.id,
        user_name=current_user.name,
        type=ActivityTypeEnum.TASK_UPDATED,
    )
    db.add(activity)
    db.commit()
    
    return updated


@router.post("/{task_id}/updates", response_model=WorkUpdateOut, status_code=status.HTTP_201_CREATED)
def add_work_update(
    task_id: str,
    update_in: WorkUpdateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    if not task:
        raise EntityNotFoundException("Task", task_id)

    work_update = WorkUpdate(
        id=f"wu-{uuid.uuid4().hex[:6]}",
        task_id=task_id,
        worker_id=current_user.id,
        description=update_in.description,
    )
    db.add(work_update)
    db.commit()
    db.refresh(work_update)
    return work_update
