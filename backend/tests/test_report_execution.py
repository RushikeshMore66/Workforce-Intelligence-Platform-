import uuid
from datetime import datetime, timedelta, timezone

import pytest
from dateutil.relativedelta import relativedelta
from sqlalchemy.exc import IntegrityError

from app.models.project import Project, ProjectStatusEnum
from app.models.report_run import ReportRun, ReportRunStatusEnum, TriggerTypeEnum
from app.models.report_schedule import (
    ReportFormatEnum,
    ReportFrequencyEnum,
    ReportSchedule,
    ReportTypeEnum,
)
from app.services.report_execution_service import ReportExecutionService
from app.services.report_run_service import ReportRunService
from app.services.report_scheduling_utils import calculate_next_run_at


def test_daily_next_run_calculation():
    current = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    now = datetime(2026, 1, 1, 15, 0, tzinfo=timezone.utc)
    next_dt = calculate_next_run_at(current, ReportFrequencyEnum.DAILY, now)
    assert next_dt == datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc)


def test_weekly_next_run_calculation():
    current = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    now = datetime(2026, 1, 1, 15, 0, tzinfo=timezone.utc)
    next_dt = calculate_next_run_at(current, ReportFrequencyEnum.WEEKLY, now)
    assert next_dt == datetime(2026, 1, 8, 10, 0, tzinfo=timezone.utc)


def test_monthly_next_run_calculation():
    current = datetime(2026, 1, 31, 10, 0, tzinfo=timezone.utc)
    now = datetime(2026, 1, 31, 15, 0, tzinfo=timezone.utc)
    next_dt = calculate_next_run_at(current, ReportFrequencyEnum.MONTHLY, now)
    # Jan 31 + 1 month = Feb 28
    assert next_dt == datetime(2026, 2, 28, 10, 0, tzinfo=timezone.utc)


def test_missed_schedule_advances_into_future():
    current = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    now = datetime(2026, 1, 5, 15, 0, tzinfo=timezone.utc)
    # missed 4 days
    next_dt = calculate_next_run_at(current, ReportFrequencyEnum.DAILY, now)
    assert next_dt == datetime(2026, 1, 6, 10, 0, tzinfo=timezone.utc)


def create_schedule(db_session, **kwargs):
    fields = dict(
        id=f"sch_{uuid.uuid4().hex[:12]}",
        name="Test Schedule",
        report_type=ReportTypeEnum.ORGANIZATION,
        export_format=ReportFormatEnum.CSV,
        frequency=ReportFrequencyEnum.DAILY,
        timezone="UTC",
        next_run_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    fields.update(kwargs)
    sch = ReportSchedule(**fields)
    db_session.add(sch)
    db_session.commit()
    return sch


def test_successful_scheduled_execution(db_session):
    sch = create_schedule(db_session)
    original_next = sch.next_run_at

    svc = ReportExecutionService(db_session)
    run = svc.execute_scheduled(sch)

    assert run.status == ReportRunStatusEnum.COMPLETED
    assert run.trigger_type == TriggerTypeEnum.SCHEDULED
    assert run.scheduled_for == original_next
    assert run.output_path is not None
    assert run.output_filename is not None

    # check advancement
    db_session.refresh(sch)
    assert sch.last_run_at == original_next
    assert sch.next_run_at > original_next


def test_successful_manual_execution(db_session):
    sch = create_schedule(db_session)
    original_next = sch.next_run_at

    svc = ReportExecutionService(db_session)
    run = svc.execute_manual(sch)

    assert run.status == ReportRunStatusEnum.COMPLETED
    assert run.trigger_type == TriggerTypeEnum.MANUAL
    assert run.scheduled_for is None
    assert run.execution_key is not None

    # manual does not advance schedule
    db_session.refresh(sch)
    assert sch.next_run_at == original_next
    assert sch.last_run_at is None


def test_deleted_project_scope(db_session):
    sch = create_schedule(
        db_session, report_type=ReportTypeEnum.PROJECT, scope_id="deleted_id"
    )
    svc = ReportExecutionService(db_session)
    run = svc.execute_scheduled(sch)

    assert run.status == ReportRunStatusEnum.FAILED
    assert "not found" in run.error_message.lower()
    
    # Internal error doesn't leak
    assert "EntityNotFoundException" not in run.error_message


def test_duplicate_scheduled_run_protection(db_session):
    # Note: SQLite does not support SKIP LOCKED, but we test the unique constraint directly.
    sch = create_schedule(db_session)
    dt = datetime.now(timezone.utc)

    run1 = ReportRunService.create_scheduled_run(db_session, sch.id, dt)
    db_session.commit()

    with pytest.raises(IntegrityError):
        run2 = ReportRunService.create_scheduled_run(db_session, sch.id, dt)
        db_session.commit()


def test_paused_schedule_not_executed(db_session):
    sch = create_schedule(db_session, is_active=False)
    svc = ReportExecutionService(db_session)

    with pytest.raises(ValueError, match="inactive schedule"):
        svc.execute_scheduled(sch)


def test_stale_running_run_recovery(db_session):
    sch = create_schedule(db_session)
    run = ReportRunService.create_scheduled_run(
        db_session, sch.id, datetime.now(timezone.utc)
    )
    db_session.commit()

    ReportRunService.mark_running(db_session, run.id)
    # backdate started_at manually to simulate stale run
    run.started_at = datetime.now(timezone.utc) - timedelta(hours=2)
    db_session.commit()

    recovered = ReportRunService.recover_stale_runs(db_session, timeout_minutes=60)
    assert recovered == 1

    db_session.refresh(run)
    assert run.status == ReportRunStatusEnum.FAILED
    assert "timed out" in run.error_message


def test_two_manual_executions_independent(db_session):
    sch = create_schedule(db_session)
    svc = ReportExecutionService(db_session)

    run1 = svc.execute_manual(sch)
    run2 = svc.execute_manual(sch)

    assert run1.id != run2.id
    assert run1.status == ReportRunStatusEnum.COMPLETED
    assert run2.status == ReportRunStatusEnum.COMPLETED
