import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ReportRunStatusEnum(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportRun(Base):
    __tablename__ = "report_runs"

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
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    schedule = relationship("ReportSchedule", back_populates="runs")
