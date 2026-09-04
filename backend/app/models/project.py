import enum
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text
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

    id = Column(
        String,
        primary_key=True,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
        index=True,
    )

    client = Column(
        String,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    start_date = Column(
        Date,
        nullable=False,
        index=True,
    )

    deadline = Column(
        Date,
        nullable=False,
        index=True,
    )

    priority = Column(
        Enum(
            ProjectPriorityEnum,
            name="project_priority_enum",
        ),
        nullable=False,
        default=ProjectPriorityEnum.MEDIUM,
        index=True,
    )

    supervisor_id = Column(
        String,
        ForeignKey(
            "supervisors.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # New projects begin in PLANNED state.
    # The service layer controls valid lifecycle transitions.
    status = Column(
        Enum(
            ProjectStatusEnum,
            name="project_status_enum",
        ),
        nullable=False,
        default=ProjectStatusEnum.PLANNED,
        index=True,
    )

    health = Column(
        Enum(
            ProjectHealthEnum,
            name="project_health_enum",
        ),
        nullable=False,
        default=ProjectHealthEnum.ON_TRACK,
        index=True,
    )

    # Cached/derived progress value maintained by the service layer.
    # It represents task completion percentage, not an independent source of truth.
    progress = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    supervisor = relationship(
        "Supervisor",
        back_populates="projects",
        foreign_keys=[supervisor_id],
    )

    teams = relationship(
        "Team",
        secondary=team_projects,
        back_populates="projects",
    )

    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    blockers = relationship(
        "Blocker",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    activities = relationship(
        "ProjectActivity",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectActivity.timestamp.desc()",
    )
