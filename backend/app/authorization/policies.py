from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User, UserRoleEnum, Supervisor, TeamLeader, Worker
from app.models.project import Project
from app.models.blocker import Blocker
from app.models.notification import Notification
from app.core.exceptions import PermissionDeniedException, EntityNotFoundException

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
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise EntityNotFoundException("Project", project_id)

    if user.role == UserRoleEnum.OWNER:
        return project

    if user.role == UserRoleEnum.SUPERVISOR:
        sup = _get_supervisor_profile(user, db)
        if sup and project.supervisor_id == sup.id:
            return project
        raise PermissionDeniedException("You are not authorized to access this project.")

    if user.role == UserRoleEnum.TEAM_LEADER:
        leader = _get_team_leader_profile(user, db)
        if leader and leader.team:
            project_ids = {p.id for p in leader.team.projects}
            if project_id in project_ids:
                return project
        raise PermissionDeniedException("You are not authorized to access this project.")

    if user.role == UserRoleEnum.WORKER:
        worker = _get_worker_profile(user, db)
        if worker and worker.team:
            project_ids = {p.id for p in worker.team.projects}
            if project_id in project_ids:
                return project
        raise PermissionDeniedException("You are not authorized to access this project.")

    raise PermissionDeniedException("Access denied.")

def authorize_worker_access(worker_id: str, user: User, db: Session) -> Worker:
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
        raise PermissionDeniedException("You are not authorized to access this worker.")

    if user.role == UserRoleEnum.TEAM_LEADER:
        leader = _get_team_leader_profile(user, db)
        if leader:
            leader_worker_ids = {w.id for w in leader.workers}
            if worker_id in leader_worker_ids:
                return worker
        raise PermissionDeniedException("You are not authorized to access this worker.")

    if user.role == UserRoleEnum.WORKER:
        own_worker = _get_worker_profile(user, db)
        if own_worker and own_worker.id == worker_id:
            return worker
        raise PermissionDeniedException("Workers may only access their own profile.")

    raise PermissionDeniedException("Access denied.")

def authorize_team_access(team_id: str, user: User, db: Session):
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
    from app.models.task import Task
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
        raise PermissionDeniedException("You are not authorized to access this task.")

    if user.role == UserRoleEnum.TEAM_LEADER:
        leader = _get_team_leader_profile(user, db)
        if leader and leader.team:
            project_ids = {p.id for p in leader.team.projects}
            if task.project_id in project_ids:
                return task
        raise PermissionDeniedException("You are not authorized to access this task.")

    if user.role == UserRoleEnum.WORKER:
        worker = _get_worker_profile(user, db)
        if worker and task.assignee_id == worker.id:
            return task
        raise PermissionDeniedException("Workers may only access their own assigned tasks.")

    raise PermissionDeniedException("Access denied.")

def authorize_blocker_access(blocker_id: str, user: User, db: Session) -> Blocker:
    blocker = db.query(Blocker).filter(Blocker.id == blocker_id).first()
    if not blocker:
        raise EntityNotFoundException("Blocker", blocker_id)
    authorize_project_access(blocker.project_id, user, db)
    return blocker

def authorize_notification_ownership(notification_id: str, user: User, db: Session) -> Notification:
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise EntityNotFoundException("Notification", notification_id)
    if notif.user_id != user.id:
        raise PermissionDeniedException("You are not authorized to modify this notification.")
    return notif
