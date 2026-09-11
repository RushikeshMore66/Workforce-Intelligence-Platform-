from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.schemas.task import TaskOut
from app.schemas.blocker import BlockerOut
from app.schemas.activity import ActivityOut
from app.schemas.analytics import ProjectAnalyticsOut
from app.schemas.common import ProjectStatus, ProjectHealth, ProjectPriority
from app.services.project_service import ProjectService
from app.services.project_analytics_service import ProjectAnalyticsService
from app.repositories.task_repo import TaskRepository
from app.repositories.blocker_repo import BlockerRepository
from app.models.activity import ProjectActivity
from app.models.project import Project
from app.models.user import User, UserRoleEnum, Supervisor, TeamLeader, Worker
from app.auth.dependencies import (
    get_current_user,
    require_supervisor,
    authorize_project_access,
    _get_supervisor_profile,
    _get_team_leader_profile,
    _get_worker_profile,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=List[ProjectOut])
def get_projects(
    search: Optional[str] = Query(None),
    status: Optional[ProjectStatus] = Query(None),
    health: Optional[ProjectHealth] = Query(None),
    priority: Optional[ProjectPriority] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List projects scoped to the authenticated user's authorization level.

    OWNER      → all projects.
    SUPERVISOR → only projects assigned to them.
    TEAM_LEADER→ only projects their team is assigned to.
    WORKER     → only projects their team is assigned to.
    """
    service = ProjectService(db)
    all_projects = service.get_projects(
        search=search, status=status, health=health, priority=priority
    )

    if current_user.role == UserRoleEnum.OWNER:
        return all_projects

    if current_user.role == UserRoleEnum.SUPERVISOR:
        sup = _get_supervisor_profile(current_user, db)
        if not sup:
            return []
        return [p for p in all_projects if p.supervisor_id == sup.id]

    if current_user.role == UserRoleEnum.TEAM_LEADER:
        leader = _get_team_leader_profile(current_user, db)
        if not leader or not leader.team:
            return []
        allowed_ids = {p.id for p in leader.team.projects}
        return [p for p in all_projects if p.id in allowed_ids]

    if current_user.role == UserRoleEnum.WORKER:
        worker = _get_worker_profile(current_user, db)
        if not worker or not worker.team:
            return []
        allowed_ids = {p.id for p in worker.team.projects}
        return [p for p in all_projects if p.id in allowed_ids]

    return []


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a single project. Raises 403 if the user cannot access it."""
    return authorize_project_access(project_id, current_user, db)


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
    current_user: User = Depends(require_supervisor),
):
    """Update a project. SUPERVISOR may only update projects assigned to them."""
    # Raises 403 if the supervisor is not assigned to this project
    authorize_project_access(project_id, current_user, db)
    service = ProjectService(db)
    return service.update_project(project_id, project_in)


@router.get("/{project_id}/tasks", response_model=List[TaskOut])
def get_project_tasks(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    authorize_project_access(project_id, current_user, db)
    repo = TaskRepository(db)
    return repo.get_by_project(project_id)


@router.get("/{project_id}/blockers", response_model=List[BlockerOut])
def get_project_blockers(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    authorize_project_access(project_id, current_user, db)
    repo = BlockerRepository(db)
    return repo.get_by_project(project_id)


@router.get("/{project_id}/activities", response_model=List[ActivityOut])
def get_project_activities(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    authorize_project_access(project_id, current_user, db)
    return (
        db.query(ProjectActivity)
        .filter(ProjectActivity.project_id == project_id)
        .order_by(ProjectActivity.timestamp.desc())
        .all()
    )


@router.get("/{project_id}/analytics", response_model=ProjectAnalyticsOut)
def get_project_analytics_data(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get deterministic analytics data for a specific project."""
    authorize_project_access(project_id, current_user, db)
    
    service = ProjectAnalyticsService(db)
    return service.get_project_analytics(project_id)
