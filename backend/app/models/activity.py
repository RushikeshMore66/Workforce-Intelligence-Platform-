import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ActivityTypeEnum(str, enum.Enum):
    PROJECT_CREATED = "PROJECT_CREATED"
    PROJECT_UPDATED = "PROJECT_UPDATED"
    PROJECT_STATUS_CHANGED = "PROJECT_STATUS_CHANGED"
    PROJECT_ASSIGNED = "PROJECT_ASSIGNED"

    TASK_CREATED = "TASK_CREATED"
    TASK_UPDATED = "TASK_UPDATED"
    TASK_ASSIGNED = "TASK_ASSIGNED"
    TASK_STATUS_CHANGED = "TASK_STATUS_CHANGED"
    TASK_COMPLETED = "TASK_COMPLETED"

    WORK_UPDATE_ADDED = "WORK_UPDATE_ADDED"

    BLOCKER_REPORTED = "BLOCKER_REPORTED"
    BLOCKER_RESOLVED = "BLOCKER_RESOLVED"

    TEAM_CREATED = "TEAM_CREATED"
    TEAM_UPDATED = "TEAM_UPDATED"
    MEMBER_ADDED = "MEMBER_ADDED"
    MEMBER_REMOVED = "MEMBER_REMOVED"

    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"


class ProjectActivity(Base):
    __tablename__ = "project_activities"

    id = Column(
        String,
        primary_key=True,
        index=True,
    )

    project_id = Column(
        String,
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    description = Column(
        Text,
        nullable=False,
    )

    user_id = Column(
        String,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # Snapshot of the user's name at event creation time.
    # This keeps historical activity readable even if the user is later removed.
    user_name = Column(
        String,
        nullable=False,
    )

    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    type = Column(
        Enum(
            ActivityTypeEnum,
            name="activity_type_enum",
        ),
        nullable=False,
        index=True,
    )

    project = relationship(
        "Project",
        back_populates="activities",
    )

    user = relationship(
        "User",
        back_populates="activities",
        foreign_keys=[user_id],
    )
