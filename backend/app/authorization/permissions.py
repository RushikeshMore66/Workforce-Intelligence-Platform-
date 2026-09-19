from enum import Enum

class Permission(str, Enum):
    ORGANIZATION_VIEW = "organization:view"
    ORGANIZATION_UPDATE = "organization:update"

    OWNER_VIEW = "owner:view"
    OWNER_CREATE = "owner:create"
    OWNER_UPDATE = "owner:update"
    OWNER_DEACTIVATE = "owner:deactivate"

    SUPERVISOR_VIEW = "supervisor:view"
    SUPERVISOR_CREATE = "supervisor:create"
    SUPERVISOR_UPDATE = "supervisor:update"
    SUPERVISOR_DEACTIVATE = "supervisor:deactivate"

    TEAM_VIEW = "team:view"
    TEAM_CREATE = "team:create"
    TEAM_UPDATE = "team:update"
    TEAM_DELETE = "team:delete"
    TEAM_MEMBERS_MANAGE = "team:members_manage"

    PROJECT_VIEW = "project:view"
    PROJECT_CREATE = "project:create"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    PROJECT_ASSIGN = "project:assign"

    WORKER_VIEW = "worker:view"
    WORKER_CREATE = "worker:create"
    WORKER_UPDATE = "worker:update"
    WORKER_DEACTIVATE = "worker:deactivate"

    TASK_VIEW = "task:view"
    TASK_CREATE = "task:create"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"

    REPORT_VIEW = "report:view"
    REPORT_EXPORT = "report:export"

    ANALYTICS_VIEW = "analytics:view"
    INTELLIGENCE_VIEW = "intelligence:view"
