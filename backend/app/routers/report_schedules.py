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


@router.post(
    "/schedules/{schedule_id}/run-now",
    response_model=ReportRunOut,
    status_code=status.HTTP_201_CREATED,
)
def run_now(
    schedule_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    schedule = ReportScheduleService(db).get_schedule(schedule_id)
    from fastapi import HTTPException
    
    if not schedule.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot manually run a paused or inactive schedule",
        )
    
    from app.services.report_execution_service import ReportExecutionService
    return ReportExecutionService(db).execute_manual(schedule)


@router.get(
    "/runs/{run_id}/download",
)
def download_run(
    run_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    from fastapi import HTTPException
    from fastapi.responses import FileResponse
    from app.models.report_run import ReportRunStatusEnum
    from app.services.report_storage_service import ReportStorageService

    run = ReportRunService(db).get_run(run_id)

    if run.status != ReportRunStatusEnum.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot download report in status: {run.status}",
        )

    if not run.output_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report output file not found",
        )

    from app.config import settings

    try:
        storage_service = ReportStorageService(settings.REPORT_STORAGE_PATH)
        # If run.output_path is relative, it should be resolved relative to storage_root.
        # But wait, resolve_safe currently takes the path as is.
        # Let's construct the absolute path first or let resolve_safe handle it if it expects an absolute path.
        # Ah, resolve_safe is implemented as Path(path).resolve().relative_to(self.storage_root).
        # We need to construct the full path first: self.storage_root / run.output_path
        
        full_path = storage_service.storage_root / run.output_path
        resolved_path = storage_service.resolve_safe(full_path)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report output file not found",
        )

    if not resolved_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report output file not found",
        )

    filename = run.output_filename or resolved_path.name

    return FileResponse(
        path=resolved_path,
        filename=filename,
        content_disposition_type="attachment",
    )
