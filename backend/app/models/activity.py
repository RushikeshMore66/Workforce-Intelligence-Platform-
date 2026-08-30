import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ActivityTypeEnum(str, enum.Enum):
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_UPDATED = "TASK_UPDATED"
    BLOCKER_REPORTED = "BLOCKER_REPORTED"
    BLOCKER_RESOLVED = "BLOCKER_RESOLVED"
    PROJECT_UPDATED = "PROJECT_UPDATED"
    MEMBER_ADDED = "MEMBER_ADDED"


class ProjectActivity(Base):
    __tablename__ = "project_activities"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_name = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    type = Column(Enum(ActivityTypeEnum), nullable=False)

    project = relationship("Project", back_populates="activities")
