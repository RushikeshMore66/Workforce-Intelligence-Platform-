import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Enum, Boolean, DateTime, ForeignKey
from app.database import Base


class NotificationTypeEnum(str, enum.Enum):
    PROJECT_ALERT = "PROJECT_ALERT"
    BLOCKER = "BLOCKER"
    DEADLINE = "DEADLINE"
    TEAM_UPDATE = "TEAM_UPDATE"
    SYSTEM = "SYSTEM"


class NotificationPriorityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    type = Column(Enum(NotificationTypeEnum), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    project_id = Column(String, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # recipient
    read = Column(Boolean, default=False, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    priority = Column(Enum(NotificationPriorityEnum), default=NotificationPriorityEnum.MEDIUM, nullable=False)
