import enum
from datetime import date

from sqlalchemy import Column, Date, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class BlockerStatusEnum(str, enum.Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class Blocker(Base):
    __tablename__ = "blockers"

    id = Column(
        String,
        primary_key=True,
        index=True,
    )

    project_id = Column(
        String,
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    task_id = Column(
        String,
        ForeignKey(
            "tasks.id",
            ondelete="SET NULL",
        ),
        nullable=True,
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

    reported_by_id = Column(
        String,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    team_id = Column(
        String,
        ForeignKey(
            "teams.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    created_date = Column(
        Date,
        nullable=False,
        default=date.today,
        index=True,
    )

    resolved_date = Column(
        Date,
        nullable=True,
    )

    status = Column(
        Enum(
            BlockerStatusEnum,
            name="blocker_status_enum",
        ),
        nullable=False,
        default=BlockerStatusEnum.OPEN,
        index=True,
    )

    project = relationship(
        "Project",
        back_populates="blockers",
    )

    task = relationship(
        "Task",
        back_populates="blockers",
    )

    reported_by = relationship(
        "User",
        foreign_keys=[reported_by_id],
    )

    team = relationship(
        "Team",
        foreign_keys=[team_id],
    )
