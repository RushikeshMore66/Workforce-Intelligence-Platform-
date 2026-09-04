from datetime import datetime
import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from app.database import Base


class UserRoleEnum(str, enum.Enum):
    OWNER = "OWNER"
    SUPERVISOR = "SUPERVISOR"
    TEAM_LEADER = "TEAM_LEADER"
    WORKER = "WORKER"


class WorkerStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    UNAVAILABLE = "UNAVAILABLE"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(
        Enum(UserRoleEnum, name="user_role_enum"),
        nullable=False,
        default=UserRoleEnum.WORKER,
        index=True,
    )
    avatar_initials = Column(String(5), nullable=False)
    company = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    supervisor_profile = relationship(
        "Supervisor",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    team_leader_profile = relationship(
        "TeamLeader",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    worker_profile = relationship(
        "Worker",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    activities = relationship(
        "ProjectActivity",
        back_populates="user",
        foreign_keys="ProjectActivity.user_id",
    )
    notifications = relationship(
        "Notification",
        back_populates="user",
        foreign_keys="Notification.user_id",
        cascade="all, delete-orphan",
    )


class Supervisor(Base):
    __tablename__ = "supervisors"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    user = relationship("User", back_populates="supervisor_profile")
    projects = relationship("Project", back_populates="supervisor")
    teams = relationship("Team", back_populates="supervisor")
    workers = relationship("Worker", back_populates="supervisor")


class TeamLeader(Base):
    __tablename__ = "team_leaders"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    # A team leader leads at most one team. TeamLeader.team_id is the single
    # source of truth for this relationship; Team does not store a duplicate FK.
    team_id = Column(
        String,
        ForeignKey("teams.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        index=True,
    )

    user = relationship("User", back_populates="team_leader_profile")
    team = relationship(
        "Team",
        back_populates="leader",
        foreign_keys=[team_id],
    )
    workers = relationship("Worker", back_populates="team_leader")


class Worker(Base):
    __tablename__ = "workers"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    role = Column(String, nullable=False)
    team_id = Column(
        String,
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # Kept as an explicit assignment so a worker's leadership/supervisor scope
    # can be validated by the service layer when organizational structures vary.
    team_leader_id = Column(
        String,
        ForeignKey("team_leaders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    supervisor_id = Column(
        String,
        ForeignKey("supervisors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status = Column(
        Enum(WorkerStatusEnum, name="worker_status_enum"),
        nullable=False,
        default=WorkerStatusEnum.ACTIVE,
        index=True,
    )
    active_project_id = Column(
        String,
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    user = relationship("User", back_populates="worker_profile")
    team = relationship("Team", back_populates="workers", foreign_keys=[team_id])
    team_leader = relationship(
        "TeamLeader",
        back_populates="workers",
        foreign_keys=[team_leader_id],
    )
    supervisor = relationship("Supervisor", back_populates="workers")
    active_project = relationship("Project", foreign_keys=[active_project_id])
    tasks = relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assignee_id",
    )
    work_updates = relationship(
        "WorkUpdate",
        back_populates="worker",
        foreign_keys="WorkUpdate.worker_id",
        cascade="all, delete-orphan",
    )
