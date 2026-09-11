import uuid
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.report_schedule import ReportSchedule, ReportTypeEnum
from app.models.team import Team
from app.models.user import Worker
from app.schemas.report_schedules import ReportScheduleCreate, ReportScheduleUpdate


class ReportScheduleService:
    def __init__(self, db: Session):
        self.db = db

    def _validate_scope(self, report_type: ReportTypeEnum, scope_id: Optional[str]) -> None:
        if report_type == ReportTypeEnum.ORGANIZATION:
            if scope_id is not None:
                raise HTTPException(status_code=400, detail="Organization report cannot have a scope_id")
        elif report_type == ReportTypeEnum.ACTIVITY:
            # scope_id is optional for activity
            if scope_id:
                # If provided, it could be a worker, project, or team.
                # In a real system, we'd check if it matches ANY of them, or we'd require a scope_type.
                # For this foundation, we just verify it exists in at least one.
                exists = (
                    self.db.query(Worker).filter(Worker.id == scope_id).first() or
                    self.db.query(Project).filter(Project.id == scope_id).first() or
                    self.db.query(Team).filter(Team.id == scope_id).first()
                )
                if not exists:
                    raise HTTPException(status_code=400, detail=f"Invalid scope_id {scope_id} for activity report")
        else:
            if scope_id is None:
                raise HTTPException(status_code=400, detail=f"scope_id is required for {report_type.value} report")
            
            if report_type == ReportTypeEnum.PROJECT:
                if not self.db.query(Project).filter(Project.id == scope_id).first():
                    raise HTTPException(status_code=400, detail=f"Project with id {scope_id} not found")
            elif report_type == ReportTypeEnum.WORKER:
                if not self.db.query(Worker).filter(Worker.id == scope_id).first():
                    raise HTTPException(status_code=400, detail=f"Worker with id {scope_id} not found")
            elif report_type == ReportTypeEnum.TEAM:
                if not self.db.query(Team).filter(Team.id == scope_id).first():
                    raise HTTPException(status_code=400, detail=f"Team with id {scope_id} not found")

    def create_schedule(self, data: ReportScheduleCreate, user_id: str) -> ReportSchedule:
        self._validate_scope(data.report_type, data.scope_id)
        
        db_obj = ReportSchedule(
            id=str(uuid.uuid4()),
            name=data.name,
            report_type=data.report_type,
            scope_id=data.scope_id,
            export_format=data.export_format,
            frequency=data.frequency,
            timezone=data.timezone,
            next_run_at=data.next_run_at,
            is_active=True,
            created_by_user_id=user_id,
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def list_schedules(self) -> List[ReportSchedule]:
        return self.db.query(ReportSchedule).order_by(ReportSchedule.created_at.desc()).all()

    def get_schedule(self, schedule_id: str) -> ReportSchedule:
        db_obj = self.db.query(ReportSchedule).filter(ReportSchedule.id == schedule_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Report schedule not found")
        return db_obj

    def update_schedule(self, schedule_id: str, data: ReportScheduleUpdate) -> ReportSchedule:
        db_obj = self.get_schedule(schedule_id)
        
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return db_obj
            
        for key, value in update_data.items():
            setattr(db_obj, key, value)
            
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def pause_schedule(self, schedule_id: str) -> ReportSchedule:
        db_obj = self.get_schedule(schedule_id)
        if db_obj.is_active:
            db_obj.is_active = False
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def resume_schedule(self, schedule_id: str) -> ReportSchedule:
        db_obj = self.get_schedule(schedule_id)
        if not db_obj.is_active:
            db_obj.is_active = True
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def delete_schedule(self, schedule_id: str) -> None:
        db_obj = self.get_schedule(schedule_id)
        self.db.delete(db_obj)
        self.db.commit()
