import enum
from pydantic import BaseModel, ConfigDict


class UserRole(str, enum.Enum):
    OWNER = "OWNER"
    SUPERVISOR = "SUPERVISOR"
    TEAM_LEADER = "TEAM_LEADER"
    WORKER = "WORKER"


class ProjectStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ProjectHealth(str, enum.Enum):
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    DELAYED = "DELAYED"


class ProjectPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class BlockerStatus(str, enum.Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class WorkerStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    UNAVAILABLE = "UNAVAILABLE"


class NotificationType(str, enum.Enum):
    PROJECT_ALERT = "PROJECT_ALERT"
    BLOCKER = "BLOCKER"
    DEADLINE = "DEADLINE"
    TEAM_UPDATE = "TEAM_UPDATE"
    SYSTEM = "SYSTEM"


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
