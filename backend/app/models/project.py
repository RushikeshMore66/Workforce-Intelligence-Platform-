import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Enum, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.team import team_projects


class ProjectStatusEnum(str, enum.Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ProjectHealthEnum(str, enum.Enum):
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    DELAYED = "DELAYED"


class ProjectPriorityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    client = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    deadline = Column(Date, nullable=False)
    priority = Column(Enum(ProjectPriorityEnum), default=ProjectPriorityEnum.MEDIUM, nullable=False)
    supervisor_id = Column(String, ForeignKey("supervisors.id", ondelete="SET NULL"), nullable=True)

    status = Column(Enum(ProjectStatusEnum), default=ProjectStatusEnum.ACTIVE, nullable=False)
    health = Column(Enum(ProjectHealthEnum), default=ProjectHealthEnum.ON_TRACK, nullable=False)
    progress = Column(Integer, default=0, nullable=False)
    team_count = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    supervisor = relationship("Supervisor", back_populates="projects")
    teams = relationship("Team", secondary=team_projects, back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    blockers = relationship("Blocker", back_populates="project", cascade="all, delete-orphan")
    activities = relationship("ProjectActivity", back_populates="project", cascade="all, delete-orphan")
