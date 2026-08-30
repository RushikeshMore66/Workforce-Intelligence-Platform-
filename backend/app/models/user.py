import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Integer
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
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.WORKER, nullable=False)
    avatar_initials = Column(String(5), nullable=False)
    company = Column(String, nullable=True)  # for OWNER

    # Specific profile relationships
    supervisor_profile = relationship("Supervisor", back_populates="user", uselist=False)
    team_leader_profile = relationship("TeamLeader", back_populates="user", uselist=False)
    worker_profile = relationship("Worker", back_populates="user", uselist=False)


class Supervisor(Base):
    __tablename__ = "supervisors"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    user = relationship("User", back_populates="supervisor_profile")
    projects = relationship("Project", back_populates="supervisor")
    teams = relationship("Team", back_populates="supervisor")
    workers = relationship("Worker", back_populates="supervisor")


class TeamLeader(Base):
    __tablename__ = "team_leaders"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    team_id = Column(String, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)

    user = relationship("User", back_populates="team_leader_profile")
    team = relationship("Team", back_populates="leader", foreign_keys=[team_id])


class Worker(Base):
    __tablename__ = "workers"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    role = Column(String, nullable=False)  # e.g., Senior Backend Developer
    team_id = Column(String, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    team_leader_id = Column(String, ForeignKey("team_leaders.id", ondelete="SET NULL"), nullable=True)
    supervisor_id = Column(String, ForeignKey("supervisors.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(WorkerStatusEnum), default=WorkerStatusEnum.ACTIVE, nullable=False)
    active_project_id = Column(String, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)

    # Metrics cache columns (can also be dynamically computed)
    completed_task_count = Column(Integer, default=0)
    in_progress_task_count = Column(Integer, default=0)
    pending_task_count = Column(Integer, default=0)
    blocked_task_count = Column(Integer, default=0)

    user = relationship("User", back_populates="worker_profile")
    team = relationship("Team", back_populates="workers", foreign_keys=[team_id])
    supervisor = relationship("Supervisor", back_populates="workers")
    active_project = relationship("Project", foreign_keys=[active_project_id])
    tasks = relationship("Task", back_populates="assignee")
