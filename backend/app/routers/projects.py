from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.schemas.task import TaskOut
from app.schemas.blocker import BlockerOut
from app.schemas.activity import ActivityOut
from app.schemas.common import ProjectStatus, ProjectHealth, ProjectPriority
from app.services.project_service import ProjectService
from app.repositories.task_repo import TaskRepository
from app.repositories.blocker_repo import BlockerRepository
from app.models.activity import ProjectActivity
from app.models.user import User
from app.auth.dependencies import get_current_user, require_supervisor

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=List[ProjectOut])
def get_projects(
    search: Optional[str] = Query(None),
    status: Optional[ProjectStatus] = Query(None),
    health: Optional[ProjectHealth] = Query(None),
    priority: Optional[ProjectPriority] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = ProjectService(db)
    return service.get_projects(search=search, status=status, health=health, priority=priority)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = ProjectService(db)
    return service.get_project(project_id)


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_supervisor),
):
    service = ProjectService(db)
    return service.create_project(project_in, current_user_name=current_user.name)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_supervisor),
):
    service = ProjectService(db)
    return service.update_project(project_id, project_in)


@router.get("/{project_id}/tasks", response_model=List[TaskOut])
def get_project_tasks(
    project_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    repo = TaskRepository(db)
    return repo.get_by_project(project_id)


@router.get("/{project_id}/blockers", response_model=List[BlockerOut])
def get_project_blockers(
    project_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    repo = BlockerRepository(db)
    return repo.get_by_project(project_id)


@router.get("/{project_id}/activities", response_model=List[ActivityOut])
def get_project_activities(
    project_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return (
        db.query(ProjectActivity)
        .filter(ProjectActivity.project_id == project_id)
        .order_by(ProjectActivity.timestamp.desc())
        .all()
    )
