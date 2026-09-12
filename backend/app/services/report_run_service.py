from datetime import datetime, timezone
from typing import List
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.report_run import ReportRun, ReportRunStatusEnum, TriggerTypeEnum
from app.models.report_schedule import ReportSchedule


class ReportRunService:
    def __init__(self, db: Session):
        self.db = db

    def list_schedule_runs(self, schedule_id: str) -> List[ReportRun]:
        # Validate schedule exists
        schedule = self.db.query(ReportSchedule).filter(ReportSchedule.id == schedule_id).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Report schedule not found")
            
        return (
            self.db.query(ReportRun)
            .filter(ReportRun.schedule_id == schedule_id)
            .order_by(ReportRun.created_at.desc())
            .limit(50)
            .all()
        )

    def get_run(self, run_id: str) -> ReportRun:
        run = self.db.query(ReportRun).filter(ReportRun.id == run_id).first()
        if not run:
            raise HTTPException(status_code=404, detail="Report run not found")
        return run

    @classmethod
    def create_scheduled_run(cls, db: Session, schedule_id: str, scheduled_for: datetime) -> ReportRun:
        run = ReportRun(
            id=f"run_{uuid.uuid4().hex[:12]}",
            schedule_id=schedule_id,
            scheduled_for=scheduled_for,
            trigger_type=TriggerTypeEnum.SCHEDULED,
            status=ReportRunStatusEnum.PENDING,
            execution_key=None,
        )
        db.add(run)
        # We rely on caller to catch IntegrityError for duplicate protection
        return run

    @classmethod
    def create_manual_run(cls, db: Session, schedule_id: str) -> ReportRun:
        run = ReportRun(
            id=f"run_{uuid.uuid4().hex[:12]}",
            schedule_id=schedule_id,
            scheduled_for=None,
            trigger_type=TriggerTypeEnum.MANUAL,
            status=ReportRunStatusEnum.PENDING,
            execution_key=f"manual:{uuid.uuid4()}",
        )
        db.add(run)
        return run

    @classmethod
    def mark_running(cls, db: Session, run_id: str) -> None:
        run = db.query(ReportRun).filter(ReportRun.id == run_id).first()
        if run:
            run.status = ReportRunStatusEnum.RUNNING
            run.started_at = datetime.now(timezone.utc)

    @classmethod
    def mark_completed(cls, db: Session, run_id: str, output_path: str, output_filename: str) -> None:
        run = db.query(ReportRun).filter(ReportRun.id == run_id).first()
        if run:
            run.status = ReportRunStatusEnum.COMPLETED
            run.finished_at = datetime.now(timezone.utc)
            run.output_path = output_path
            run.output_filename = output_filename

    @classmethod
    def mark_failed(cls, db: Session, run_id: str, error_message: str) -> None:
        run = db.query(ReportRun).filter(ReportRun.id == run_id).first()
        if run:
            run.status = ReportRunStatusEnum.FAILED
            run.finished_at = datetime.now(timezone.utc)
            run.error_message = error_message

    @classmethod
    def recover_stale_runs(cls, db: Session, timeout_minutes: int) -> int:
        import datetime as dt
        timeout_threshold = datetime.now(timezone.utc) - dt.timedelta(minutes=timeout_minutes)
        
        stale_runs = (
            db.query(ReportRun)
            .filter(ReportRun.status == ReportRunStatusEnum.RUNNING)
            .filter(ReportRun.started_at < timeout_threshold)
            .all()
        )
        
        count = 0
        for run in stale_runs:
            run.status = ReportRunStatusEnum.FAILED
            run.error_message = "Execution timed out or process was interrupted"
            run.finished_at = datetime.now(timezone.utc)
            count += 1
            
        if count > 0:
            db.commit()
            
        return count
