import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Enum, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class BlockerStatusEnum(str, enum.Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class Blocker(Base):
    __tablename__ = "blockers"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    reported_by_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    team_id = Column(String, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    created_date = Column(Date, default=datetime.utcnow().date, nullable=False)
    resolved_date = Column(Date, nullable=True)
    status = Column(Enum(BlockerStatusEnum), default=BlockerStatusEnum.OPEN, nullable=False)

    project = relationship("Project", back_populates="blockers")
