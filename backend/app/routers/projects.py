from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, ProjectStatusChange
from app.schemas.task import TaskOut
from app.schemas.blocker import BlockerOut
from app.schemas.activity import ActivityOut
from app.schemas.analytics import ProjectAnalyticsOut
from app.schemas.common import ProjectStatus, ProjectHealth, ProjectPriority
from app.services.project_service import ProjectService
from app.services.project_analytics_service import ProjectAnalyticsService
from app.services.project_progress_service import ProjectProgressService
from app.services.project_workflow_service import ProjectWorkflowService
from app.repositories.task_repo import TaskRepository
from app.repositories.blocker_repo import BlockerRepository
from app.models.activity import ProjectActivity, ActivityTypeEnum
from app.models.project import Project, ProjectStatusEnum
from app.models.user import User, UserRoleEnum, Supervisor, TeamLeader, Worker
from app.auth.dependencies import get_current_user
from app.authorization.dependencies import RequirePermission
from app.authorization.permissions import Permission
from app.authorization.policies import (authorize_project_access,
    _get_supervisor_profile,
    _get_team_leader_profile,
    _get_worker_profile,)
from app.core.exceptions import PermissionDeniedException

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
    current_user: User = Depends(RequirePermission(Permission.PROJECT_CREATE)),
):
    service = ProjectService(db)
    return service.create_project(project_in, current_user_name=current_user.name)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update project metadata. SUPERVISOR may only update their own projects."""
    authorize_project_access(project_id, current_user, db)

    if current_user.role not in {
        UserRoleEnum.OWNER,
        UserRoleEnum.SUPERVISOR,
    }:
        raise PermissionDeniedException(
            "Only owners and supervisors can edit project details."
        )

    service = ProjectService(db)
    return service.update_project(project_id, project_in)


@router.post("/{project_id}/status", response_model=ProjectOut)
def change_project_status(
    project_id: str,
    status_in: ProjectStatusChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change project lifecycle status through the workflow engine.

    Validates the transition against the canonical state machine:
      PLANNED → ACTIVE | CANCELLED
      ACTIVE → ON_HOLD | COMPLETED | CANCELLED
      ON_HOLD → ACTIVE | CANCELLED

    Only OWNER and SUPERVISOR roles may call this endpoint.
    Only OWNER may cancel a project.
    ON_HOLD and CANCELLED require a non-empty reason.
    COMPLETED requires all non-cancelled tasks to be completed.
    """
    project = authorize_project_access(project_id, current_user, db)

    # Refresh derived progress before evaluating completion.
    ProjectProgressService.recalculate_project_progress(db, project.id)
    db.refresh(project)

    target_status = ProjectStatusEnum(status_in.status.value)
    ProjectWorkflowService.validate_transition(
        project=project,
        to_status=target_status,
        user=current_user,
        db=db,
        reason=status_in.reason,
    )

    old_status = project.status
    project.status = target_status

    activity = ProjectActivity(
        id=f"act-project-status-{uuid.uuid4().hex[:10]}",
        project_id=project.id,
        description=(
            f"Project '{project.name}' changed from "
            f"{old_status.value} to {project.status.value} "
            f"by {current_user.name}."
            + (
                f" Reason: {status_in.reason.strip()}"
                if status_in.reason
                else ""
            )
        ),
        user_id=current_user.id,
        user_name=current_user.name,
        type=ActivityTypeEnum.PROJECT_STATUS_CHANGED,
    )

    db.add(project)
    db.add(activity)
    db.commit()
    db.refresh(project)

    return project


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
