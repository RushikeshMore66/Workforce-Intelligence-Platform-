import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from app.database import Base


class ReportTypeEnum(str, enum.Enum):
    ORGANIZATION = "organization"
    PROJECT = "project"
    WORKER = "worker"
    TEAM = "team"
    ACTIVITY = "activity"


class ReportFormatEnum(str, enum.Enum):
    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"


class ReportFrequencyEnum(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ReportSchedule(Base):
    __tablename__ = "report_schedules"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    report_type = Column(
        Enum(ReportTypeEnum, name="report_type_enum"),
        nullable=False,
        index=True,
    )
    scope_id = Column(String, nullable=True)
    export_format = Column(
        Enum(ReportFormatEnum, name="report_format_enum"),
        nullable=False,
    )
    frequency = Column(
        Enum(ReportFrequencyEnum, name="report_frequency_enum"),
        nullable=False,
    )
    timezone = Column(String, nullable=False)
    next_run_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_by_user_id = Column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    runs = relationship(
        "ReportRun",
        back_populates="schedule",
        cascade="all, delete-orphan",
    )
