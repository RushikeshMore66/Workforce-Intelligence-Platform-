from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.jwt import decode_jwt_token
from app.models.user import User, UserRoleEnum, Supervisor, TeamLeader, Worker
from app.models.project import Project
from app.models.blocker import Blocker
from app.models.notification import Notification
from app.core.exceptions import PermissionDeniedException, EntityNotFoundException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate JWT and return the authenticated User from the database.

    Raises HTTP 401 if the token is missing, invalid, or expired.
    The user identity is always resolved from the database — never trusted
    from the token claims alone.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    payload = decode_jwt_token(token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


class RoleChecker:
    """Reusable FastAPI dependency for role-based access control.

    Raises HTTP 403 if the authenticated user's role is not in allowed_roles.
    """

    def __init__(self, allowed_roles: List[UserRoleEnum]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            raise PermissionDeniedException(
                f"Role '{user.role.value}' is not authorized for this operation."
            )
        return user


# ── Common role dependencies ──────────────────────────────────────────────────

require_owner = RoleChecker([UserRoleEnum.OWNER])
require_supervisor = RoleChecker([UserRoleEnum.OWNER, UserRoleEnum.SUPERVISOR])
require_team_lead = RoleChecker(
    [UserRoleEnum.OWNER, UserRoleEnum.SUPERVISOR, UserRoleEnum.TEAM_LEADER]
)
require_authenticated = get_current_user


# ── Resource-level authorization helpers ──────────────────────────────────────

def _get_supervisor_profile(user: User, db: Session) -> Optional[Supervisor]:
    """Return the Supervisor profile for a SUPERVISOR-role user, or None."""
    if user.role != UserRoleEnum.SUPERVISOR:
        return None
    return db.query(Supervisor).filter(Supervisor.user_id == user.id).first()


def _get_team_leader_profile(user: User, db: Session) -> Optional[TeamLeader]:
    """Return the TeamLeader profile for a TEAM_LEADER-role user, or None."""
    if user.role != UserRoleEnum.TEAM_LEADER:
        return None
    return db.query(TeamLeader).filter(TeamLeader.user_id == user.id).first()


def _get_worker_profile(user: User, db: Session) -> Optional[Worker]:
    """Return the Worker profile for a WORKER-role user, or None."""
    if user.role != UserRoleEnum.WORKER:
        return None
    return db.query(Worker).filter(Worker.user_id == user.id).first()


def authorize_project_access(project_id: str, user: User, db: Session) -> Project:
    """Verify that the current user may access the given project.

    OWNER   → any project.
    SUPERVISOR → only their assigned projects.
    TEAM_LEADER → projects assigned to their team.
    WORKER  → projects their team is assigned to.

    Raises 404 if the project does not exist, 403 if the user cannot access it.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise EntityNotFoundException("Project", project_id)

    if user.role == UserRoleEnum.OWNER:
        return project

    if user.role == UserRoleEnum.SUPERVISOR:
        sup = _get_supervisor_profile(user, db)
        if sup and project.supervisor_id == sup.id:
            return project
        raise PermissionDeniedException(
            "You are not authorized to access this project."
        )

    if user.role == UserRoleEnum.TEAM_LEADER:
        leader = _get_team_leader_profile(user, db)
        if leader and leader.team:
            # Project must be in the leader's team's project list
            project_ids = {p.id for p in leader.team.projects}
            if project_id in project_ids:
                return project
        raise PermissionDeniedException(
            "You are not authorized to access this project."
        )

    if user.role == UserRoleEnum.WORKER:
        worker = _get_worker_profile(user, db)
        if worker and worker.team:
            project_ids = {p.id for p in worker.team.projects}
            if project_id in project_ids:
                return project
        raise PermissionDeniedException(
            "You are not authorized to access this project."
        )

    raise PermissionDeniedException("Access denied.")


def authorize_worker_access(worker_id: str, user: User, db: Session) -> Worker:
    """Verify that the current user may view the given worker.

    OWNER      → any worker.
    SUPERVISOR → workers in their assigned teams.
    TEAM_LEADER→ workers in their own team.
    WORKER     → only themselves.

    Raises 404 if the worker does not exist, 403 if unauthorized.
    """
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise EntityNotFoundException("Worker", worker_id)

    if user.role == UserRoleEnum.OWNER:
        return worker

    if user.role == UserRoleEnum.SUPERVISOR:
        sup = _get_supervisor_profile(user, db)
        if sup:
            sup_worker_ids = {w.id for w in sup.workers}
            if worker_id in sup_worker_ids:
                return worker
        raise PermissionDeniedException(
            "You are not authorized to access this worker."
        )

    if user.role == UserRoleEnum.TEAM_LEADER:
        leader = _get_team_leader_profile(user, db)
        if leader:
            leader_worker_ids = {w.id for w in leader.workers}
            if worker_id in leader_worker_ids:
                return worker
        raise PermissionDeniedException(
            "You are not authorized to access this worker."
        )

    if user.role == UserRoleEnum.WORKER:
        own_worker = _get_worker_profile(user, db)
        if own_worker and own_worker.id == worker_id:
            return worker
        raise PermissionDeniedException(
            "Workers may only access their own profile."
        )

    raise PermissionDeniedException("Access denied.")


def authorize_team_access(team_id: str, user: User, db: Session):
    """Verify that the current user may access the given team.

    OWNER      → any team.
    SUPERVISOR → only their assigned teams.
    TEAM_LEADER→ only their own team.
    WORKER     → only their own team.

    Raises 404 if the team does not exist, 403 if unauthorized.
    """
    from app.models.team import Team

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise EntityNotFoundException("Team", team_id)

    if user.role == UserRoleEnum.OWNER:
        return team

    if user.role == UserRoleEnum.SUPERVISOR:
        sup = _get_supervisor_profile(user, db)
        if sup and any(t.id == team_id for t in sup.teams):
            return team
        raise PermissionDeniedException("You are not authorized to access this team.")

    if user.role == UserRoleEnum.TEAM_LEADER:
        leader = _get_team_leader_profile(user, db)
        if leader and leader.team_id == team_id:
            return team
        raise PermissionDeniedException("You are not authorized to access this team.")

    if user.role == UserRoleEnum.WORKER:
        worker = _get_worker_profile(user, db)
        if worker and worker.team_id == team_id:
            return team
        raise PermissionDeniedException("You are not authorized to access this team.")

    raise PermissionDeniedException("Access denied.")


def authorize_task_access(task_id: str, user: User, db: Session):
    """Verify that the current user may access or modify the given task.

    OWNER      → any task.
    SUPERVISOR → tasks in accessible projects.
    TEAM_LEADER→ tasks in their team's projects.
    WORKER     → only their own assigned tasks.

    Raises 404 if the task does not exist, 403 if unauthorized.
    """
    from app.models.task import Task  # local import to avoid circular imports

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise EntityNotFoundException("Task", task_id)

    if user.role == UserRoleEnum.OWNER:
        return task

    if user.role == UserRoleEnum.SUPERVISOR:
        sup = _get_supervisor_profile(user, db)
        if sup:
            project = db.query(Project).filter(Project.id == task.project_id).first()
            if project and project.supervisor_id == sup.id:
                return task
        raise PermissionDeniedException(
            "You are not authorized to access this task."
        )

    if user.role == UserRoleEnum.TEAM_LEADER:
        leader = _get_team_leader_profile(user, db)
        if leader and leader.team:
            project_ids = {p.id for p in leader.team.projects}
            if task.project_id in project_ids:
                return task
        raise PermissionDeniedException(
            "You are not authorized to access this task."
        )

    if user.role == UserRoleEnum.WORKER:
        worker = _get_worker_profile(user, db)
        if worker and task.assignee_id == worker.id:
            return task
        raise PermissionDeniedException(
            "Workers may only access their own assigned tasks."
        )

    raise PermissionDeniedException("Access denied.")


def authorize_blocker_access(blocker_id: str, user: User, db: Session) -> Blocker:
    """Verify that the current user may access the given blocker.

    Access mirrors project access: the user must be authorized to see the
    blocker's parent project.

    Raises 404 if the blocker does not exist, 403 if unauthorized.
    """
    blocker = db.query(Blocker).filter(Blocker.id == blocker_id).first()
    if not blocker:
        raise EntityNotFoundException("Blocker", blocker_id)

    # Reuse project-level scoping — if the user can see the project, they can
    # see its blockers.
    authorize_project_access(blocker.project_id, user, db)
    return blocker


def authorize_notification_ownership(notification_id: str, user: User, db: Session) -> Notification:
    """Verify that the notification belongs to the current user.

    Raises 404 if not found, 403 if it belongs to another user.
    """
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise EntityNotFoundException("Notification", notification_id)
    if notif.user_id != user.id:
        raise PermissionDeniedException(
            "You are not authorized to modify this notification."
        )
    return notif
