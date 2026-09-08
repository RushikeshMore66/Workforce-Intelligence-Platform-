import enum
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, String, Text
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
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    assignee_id = Column(String, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True, index=True)
    team_id = Column(String, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(
        Enum(TaskStatusEnum, name="task_status_enum"),
        nullable=False,
        default=TaskStatusEnum.TODO,
        index=True,
    )
    priority = Column(
        Enum(ProjectPriorityEnum, name="project_priority_enum"),
        nullable=False,
        default=ProjectPriorityEnum.MEDIUM,
        index=True,
    )
    due_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="tasks")

    assignee = relationship(
        "Worker",
        back_populates="tasks",
        foreign_keys=[assignee_id],
    )

    team = relationship("Team", foreign_keys=[team_id])

    updates = relationship(
        "WorkUpdate",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="WorkUpdate.timestamp.desc()",
    )

    blockers = relationship(
        "Blocker",
        back_populates="task",
    )


class WorkUpdate(Base):
    __tablename__ = "work_updates"

    id = Column(String, primary_key=True, index=True)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    worker_id = Column(String, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    task = relationship("Task", back_populates="updates")

    worker = relationship(
        "Worker",
        back_populates="work_updates",
        foreign_keys=[worker_id],
    )

    created_by = relationship(
        "User",
        foreign_keys=[created_by_user_id],
    )
