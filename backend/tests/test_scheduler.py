import logging
import threading
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.models.report_run import ReportRunStatusEnum
from app.scheduler import coordinator
from app.scheduler.jobs import run_scheduled_reports
from app.scheduler.scheduler import _scheduler, shutdown, start
from app.scheduler.worker import handle_signal, stop_event
from app.services.report_run_service import ReportRunService
from tests.test_report_execution import create_schedule

# Note for developers:
# SQLite does not support SELECT FOR UPDATE SKIP LOCKED.
# The production coordinator intentionally uses this PostgreSQL-compatible
# locking query. SQLite tests validate business behavior and duplicate
# constraints, while PostgreSQL integration tests are required to validate
# true concurrent locking behavior.

from app.models.report_schedule import ReportSchedule
from app.models.report_run import ReportRun

@pytest.fixture(autouse=True)
def clean_schedules(db_session):
    db_session.query(ReportRun).delete()
    db_session.query(ReportSchedule).delete()
    db_session.commit()

def test_coordinator_recovers_stale_runs(db_session):
    sch = create_schedule(db_session)
    run = ReportRunService.create_scheduled_run(
        db_session, sch.id, datetime.now(timezone.utc)
    )
    db_session.commit()

    ReportRunService.mark_running(db_session, run.id)
    # Stale it out
    run.started_at = datetime.now(timezone.utc) - timedelta(
        minutes=settings.REPORT_STALE_RUN_TIMEOUT_MINUTES + 10
    )
    db_session.commit()

    coordinator.tick(db_session)

    db_session.refresh(run)
    assert run.status == ReportRunStatusEnum.FAILED
    assert "timed out" in run.error_message


def test_coordinator_skips_paused_schedule(db_session):
    sch = create_schedule(db_session, is_active=False)

    with patch("app.scheduler.coordinator.ReportExecutionService") as MockSvc:
        coordinator.tick(db_session)
        # Should not have called execution service
        MockSvc.return_value.execute_scheduled.assert_not_called()


def test_coordinator_executes_due_schedule(db_session):
    sch = create_schedule(db_session)

    with patch("app.scheduler.coordinator.ReportExecutionService") as MockSvc:
        coordinator.tick(db_session)
        MockSvc.return_value.execute_scheduled.assert_called_once_with(sch)


def test_coordinator_skips_future_schedule(db_session):
    sch = create_schedule(
        db_session, next_run_at=datetime.now(timezone.utc) + timedelta(days=1)
    )

    with patch("app.scheduler.coordinator.ReportExecutionService") as MockSvc:
        coordinator.tick(db_session)
        MockSvc.return_value.execute_scheduled.assert_not_called()


def test_scheduler_start_is_idempotent():
    # Make sure it's stopped before test
    if _scheduler.running:
        _scheduler.shutdown(wait=False)

    start()
    jobs1 = _scheduler.get_jobs()
    assert len(jobs1) == 1

    start()
    jobs2 = _scheduler.get_jobs()
    assert len(jobs2) == 1

    # Cleanup
    shutdown()


def test_scheduler_shutdown_is_safe():
    if _scheduler.running:
        _scheduler.shutdown(wait=False)

    start()
    assert _scheduler.running is True

    shutdown()
    assert _scheduler.running is False

    # Idempotent shutdown
    shutdown()


def test_scheduler_disabled_by_default():
    assert settings.REPORT_SCHEDULER_ENABLED is False


@patch("app.scheduler.jobs.SessionLocal")
@patch("app.scheduler.jobs.tick")
def test_scheduler_job_uses_fresh_session(mock_tick, mock_session_local):
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    run_scheduled_reports()

    mock_session_local.assert_called_once()
    mock_tick.assert_called_once_with(mock_db)
    mock_db.close.assert_called_once()


@patch("app.scheduler.jobs.SessionLocal")
@patch("app.scheduler.jobs.tick")
def test_scheduler_job_handles_exception(mock_tick, mock_session_local):
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_tick.side_effect = Exception("Simulated tick failure")

    # Should not raise exception
    run_scheduled_reports()

    mock_session_local.assert_called_once()
    mock_tick.assert_called_once_with(mock_db)
    mock_db.close.assert_called_once()


def test_worker_handles_shutdown_signal():
    stop_event.clear()
    assert not stop_event.is_set()
    
    handle_signal(None, None)
    
    assert stop_event.is_set()
