from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.report_run import ReportRun
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
