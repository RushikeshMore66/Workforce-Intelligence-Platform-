from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.authorization.dependencies import RequirePermission
from app.authorization.permissions import Permission
from app.authorization.policies import (
    _get_supervisor_profile,
    _get_team_leader_profile,
    _get_worker_profile,
    authorize_project_access,
)
from app.core.exceptions import PermissionDeniedException
from app.database import get_db
from app.models.activity import ActivityTypeEnum, ProjectActivity
from app.models.project import Project, ProjectStatusEnum
from app.models.user import User, UserRoleEnum
from app.repositories.blocker_repo import BlockerRepository
from app.repositories.task_repo import TaskRepository
from app.schemas.activity import ActivityOut
from app.schemas.analytics import ProjectAnalyticsOut
from app.schemas.blocker import BlockerOut
from app.schemas.common import ProjectHealth, ProjectPriority, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectOut, ProjectStatusChange, ProjectUpdate
from app.schemas.task import TaskOut
from app.services.project_analytics_service import ProjectAnalyticsService
from app.services.project_service import ProjectService
from app.services.project_workflow_service import ProjectWorkflowService

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
    service = ProjectService(db)
    all_projects = service.get_projects(
        search=search,
        status=status,
        health=health,
        priority=priority,
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
    return authorize_project_access(project_id, current_user, db)


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission(Permission.PROJECT_CREATE)),
):
    service = ProjectService(db)
    return service.create_project(
        project_in,
        current_user_name=current_user.name,
    )


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    authorize_project_access(project_id, current_user, db)

    if current_user.role not in {
        UserRoleEnum.OWNER,
        UserRoleEnum.SUPERVISOR,
    }:
        raise PermissionDeniedException(
            "Only owners and supervisors can edit project details."
        )

    return ProjectService(db).update_project(project_id, project_in)


@router.post("/{project_id}/status", response_model=ProjectOut)
def change_project_status(
    project_id: str,
    status_in: ProjectStatusChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = authorize_project_access(project_id, current_user, db)

    ProjectWorkflowService.validate_transition(
        project=project,
        to_status=ProjectStatusEnum(status_in.status.value),
        user=current_user,
    )

    old_status = project.status
    project.status = ProjectStatusEnum(status_in.status.value)

    activity = ProjectActivity(
        id=f"act-project-status-{project.id}",
        project_id=project.id,
        description=(
            f"Project '{project.name}' changed from "
            f"{old_status.value} to {project.status.value} "
            f"by {current_user.name}."
            + (f" Reason: {status_in.reason.strip()}" if status_in.reason else "")
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
    return TaskRepository(db).get_by_project(project_id)


@router.get("/{project_id}/blockers", response_model=List[BlockerOut])
def get_project_blockers(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    authorize_project_access(project_id, current_user, db)
    return BlockerRepository(db).get_by_project(project_id)


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
    authorize_project_access(project_id, current_user, db)
    return ProjectAnalyticsService(db).get_project_analytics(project_id)
