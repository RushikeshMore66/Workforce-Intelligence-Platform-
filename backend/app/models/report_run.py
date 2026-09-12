import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, Index, text
from sqlalchemy.orm import relationship

from app.database import Base


class ReportRunStatusEnum(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TriggerTypeEnum(str, enum.Enum):
    SCHEDULED = "scheduled"
    MANUAL = "manual"


class ReportRun(Base):
    __tablename__ = "report_runs"
    __table_args__ = (
        Index(
            "uq_report_runs_schedule_slot",
            "schedule_id",
            "scheduled_for",
            unique=True,
            sqlite_where=text("scheduled_for IS NOT NULL"),
            postgresql_where=text("scheduled_for IS NOT NULL"),
        ),
    )

    id = Column(String, primary_key=True, index=True)
    schedule_id = Column(
        String,
        ForeignKey("report_schedules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(
        Enum(ReportRunStatusEnum, name="report_run_status_enum"),
        nullable=False,
        default=ReportRunStatusEnum.PENDING,
        index=True,
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    output_filename = Column(String, nullable=True)
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    output_path = Column(String, nullable=True)
    trigger_type = Column(
        Enum(TriggerTypeEnum, name="trigger_type_enum"),
        nullable=False,
        default=TriggerTypeEnum.SCHEDULED,
    )
    execution_key = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    schedule = relationship("ReportSchedule", back_populates="runs")
