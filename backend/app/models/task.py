import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Enum, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.project import ProjectPriorityEnum


class TaskStatusEnum(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    assignee_id = Column(String, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True)
    team_id = Column(String, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.TODO, nullable=False)
    priority = Column(Enum(ProjectPriorityEnum), default=ProjectPriorityEnum.MEDIUM, nullable=False)
    due_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="tasks")
    assignee = relationship("Worker", back_populates="tasks")
    updates = relationship("WorkUpdate", back_populates="task", cascade="all, delete-orphan")


class WorkUpdate(Base):
    __tablename__ = "work_updates"

    id = Column(String, primary_key=True, index=True)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    worker_id = Column(String, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    task = relationship("Task", back_populates="updates")
