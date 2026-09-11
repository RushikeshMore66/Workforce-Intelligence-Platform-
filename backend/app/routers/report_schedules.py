from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_owner
from app.database import get_db
from app.models.user import User
from app.schemas.report_schedules import (
    ReportRunOut,
    ReportScheduleCreate,
    ReportScheduleListItem,
    ReportScheduleOut,
    ReportScheduleUpdate,
)
from app.services.report_run_service import ReportRunService
from app.services.report_schedule_service import ReportScheduleService

router = APIRouter(prefix="/reports", tags=["Report Scheduling"])


@router.post(
    "/schedules",
    response_model=ReportScheduleOut,
    status_code=status.HTTP_201_CREATED,
)
def create_schedule(
    data: ReportScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner),
):
    return ReportScheduleService(db).create_schedule(data, current_user.id)


@router.get(
    "/schedules",
    response_model=List[ReportScheduleListItem],
)
def list_schedules(
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    return ReportScheduleService(db).list_schedules()


@router.get(
    "/schedules/{schedule_id}",
    response_model=ReportScheduleOut,
)
def get_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    return ReportScheduleService(db).get_schedule(schedule_id)


@router.patch(
    "/schedules/{schedule_id}",
    response_model=ReportScheduleOut,
)
def update_schedule(
    schedule_id: str,
    data: ReportScheduleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    return ReportScheduleService(db).update_schedule(schedule_id, data)


@router.delete(
    "/schedules/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    ReportScheduleService(db).delete_schedule(schedule_id)


@router.post(
    "/schedules/{schedule_id}/pause",
    response_model=ReportScheduleOut,
)
def pause_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    return ReportScheduleService(db).pause_schedule(schedule_id)


@router.post(
    "/schedules/{schedule_id}/resume",
    response_model=ReportScheduleOut,
)
def resume_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    return ReportScheduleService(db).resume_schedule(schedule_id)


@router.get(
    "/schedules/{schedule_id}/runs",
    response_model=List[ReportRunOut],
)
def list_schedule_runs(
    schedule_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    return ReportRunService(db).list_schedule_runs(schedule_id)


@router.get(
    "/runs/{run_id}",
    response_model=ReportRunOut,
)
def get_run(
    run_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    return ReportRunService(db).get_run(run_id)
