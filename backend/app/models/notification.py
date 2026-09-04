import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class NotificationTypeEnum(str, enum.Enum):
    PROJECT_ALERT = "PROJECT_ALERT"
    BLOCKER = "BLOCKER"
    DEADLINE = "DEADLINE"
    TASK = "TASK"
    WORK_UPDATE = "WORK_UPDATE"
    TEAM_UPDATE = "TEAM_UPDATE"
    SYSTEM = "SYSTEM"


class NotificationPriorityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        String,
        primary_key=True,
        index=True,
    )

    type = Column(
        Enum(
            NotificationTypeEnum,
            name="notification_type_enum",
        ),
        nullable=False,
        index=True,
    )

    title = Column(
        String,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=False,
    )

    project_id = Column(
        String,
        ForeignKey(
            "projects.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    user_id = Column(
        String,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    read = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    priority = Column(
        Enum(
            NotificationPriorityEnum,
            name="notification_priority_enum",
        ),
        nullable=False,
        default=NotificationPriorityEnum.MEDIUM,
        index=True,
    )

    project = relationship(
        "Project",
    )

    user = relationship(
        "User",
        back_populates="notifications",
        foreign_keys=[user_id],
    )
