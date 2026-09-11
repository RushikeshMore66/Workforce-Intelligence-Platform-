"""Reports router — deterministic, permission-safe report endpoints."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    authorize_project_access,
    authorize_team_access,
    authorize_worker_access,
    get_current_user,
    require_owner,
)
from app.database import get_db
from app.models.user import User
from app.schemas.reports import (
    ActivityReport,
    OrganizationSummaryReport,
    ProjectPerformanceReport,
    TeamPerformanceReport,
    WorkerPerformanceReport,
)
from app.services.report_service import ReportService
from app.services.report_export_service import ReportExportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/organization", response_model=OrganizationSummaryReport)
def get_organization_report(
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    """Organization-wide summary report. OWNER only."""
    return ReportService(db).get_organization_report()


@router.get("/projects/{project_id}", response_model=ProjectPerformanceReport)
def get_project_report(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Project performance report. Uses existing project access rules."""
    project = authorize_project_access(project_id, current_user, db)
    return ReportService(db).get_project_report(project)


@router.get("/workers/{worker_id}", response_model=WorkerPerformanceReport)
def get_worker_report(
    worker_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Worker performance report. Uses existing worker access rules."""
    worker = authorize_worker_access(worker_id, current_user, db)
    return ReportService(db).get_worker_report(worker)


@router.get("/teams/{team_id}", response_model=TeamPerformanceReport)
def get_team_report(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Team performance report. Uses existing team access rules."""
    team = authorize_team_access(team_id, current_user, db)
    return ReportService(db).get_team_report(team)


@router.get("/activity", response_model=ActivityReport)
def get_activity_report(
    worker_id: Optional[str] = Query(default=None),
    project_id: Optional[str] = Query(default=None),
    team_id: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Activity feed report with optional filters.

    Authorization: Scope is enforced per filter.
    - If worker_id provided: authorize_worker_access applied.
    - If project_id provided: authorize_project_access applied.
    - If team_id provided: authorize_team_access applied.
    - If no scope filter: OWNER sees all; others see their scoped updates.
    """
    from app.models.user import UserRoleEnum, Worker, TeamLeader
    from app.auth.dependencies import (
        _get_worker_profile,
        _get_team_leader_profile,
        _get_supervisor_profile,
    )

    # Validate requested scopes match caller permissions
    if worker_id:
        authorize_worker_access(worker_id, current_user, db)
    if project_id:
        authorize_project_access(project_id, current_user, db)
    if team_id:
        authorize_team_access(team_id, current_user, db)

    # If no explicit scope, apply implicit scoping by role
    effective_worker_id = worker_id
    effective_project_id = project_id
    effective_team_id = team_id

    if not worker_id and not project_id and not team_id:
        if current_user.role == UserRoleEnum.WORKER:
            own = _get_worker_profile(current_user, db)
            effective_worker_id = own.id if own else None
        elif current_user.role == UserRoleEnum.TEAM_LEADER:
            leader = _get_team_leader_profile(current_user, db)
            effective_team_id = leader.team_id if leader else None
        # OWNER and SUPERVISOR get all (no implicit filter)

    return ReportService(db).get_activity_report(
        worker_id=effective_worker_id,
        project_id=effective_project_id,
        team_id=effective_team_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )


# ─── Export endpoints ─────────────────────────────────────────────────────────


def _stream(data: bytes, content_type: str, filename: str) -> StreamingResponse:
    import io
    return StreamingResponse(
        io.BytesIO(data),
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/organization/export")
def export_organization_report(
    format: str = Query(default="csv"),
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    """Export organization-wide summary report. OWNER only."""
    report = ReportService(db).get_organization_report()
    data, ctype, fname = ReportExportService().export_organization(report, format)
    return _stream(data, ctype, fname)


@router.get("/projects/{project_id}/export")
def export_project_report(
    project_id: str,
    format: str = Query(default="csv"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export project performance report. Uses existing project access rules."""
    project = authorize_project_access(project_id, current_user, db)
    report = ReportService(db).get_project_report(project)
    data, ctype, fname = ReportExportService().export_project(report, format)
    return _stream(data, ctype, fname)


@router.get("/workers/{worker_id}/export")
def export_worker_report(
    worker_id: str,
    format: str = Query(default="csv"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export worker performance report. Uses existing worker access rules."""
    worker = authorize_worker_access(worker_id, current_user, db)
    report = ReportService(db).get_worker_report(worker)
    data, ctype, fname = ReportExportService().export_worker(report, format)
    return _stream(data, ctype, fname)


@router.get("/teams/{team_id}/export")
def export_team_report(
    team_id: str,
    format: str = Query(default="csv"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export team performance report. Uses existing team access rules."""
    team = authorize_team_access(team_id, current_user, db)
    report = ReportService(db).get_team_report(team)
    data, ctype, fname = ReportExportService().export_team(report, format)
    return _stream(data, ctype, fname)


@router.get("/activity/export")
def export_activity_report(
    worker_id: Optional[str] = Query(default=None),
    project_id: Optional[str] = Query(default=None),
    team_id: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    limit: int = Query(default=50, ge=1),
    offset: int = Query(default=0, ge=0),
    format: str = Query(default="csv"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export activity report with optional filters.
    Maximum limit=1000; returns HTTP 400 above that.
    Reuses same authorization logic as GET /activity.
    """
    from fastapi import HTTPException
    from app.models.user import UserRoleEnum
    from app.auth.dependencies import _get_worker_profile, _get_team_leader_profile

    if limit > 1000:
        raise HTTPException(status_code=400, detail="Activity export limit cannot exceed 1000.")

    if worker_id:
        authorize_worker_access(worker_id, current_user, db)
    if project_id:
        authorize_project_access(project_id, current_user, db)
    if team_id:
        authorize_team_access(team_id, current_user, db)

    effective_worker_id = worker_id
    effective_project_id = project_id
    effective_team_id = team_id

    if not worker_id and not project_id and not team_id:
        if current_user.role == UserRoleEnum.WORKER:
            own = _get_worker_profile(current_user, db)
            effective_worker_id = own.id if own else None
        elif current_user.role == UserRoleEnum.TEAM_LEADER:
            leader = _get_team_leader_profile(current_user, db)
            effective_team_id = leader.team_id if leader else None

    report = ReportService(db).get_activity_report(
        worker_id=effective_worker_id,
        project_id=effective_project_id,
        team_id=effective_team_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    data, ctype, fname = ReportExportService().export_activity(report, format)
    return _stream(data, ctype, fname)
