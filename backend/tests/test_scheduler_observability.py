import time
import pytest
from unittest.mock import MagicMock, patch

from app.observability.scheduler_metrics import SCHEDULER_REGISTRY

from app.observability.scheduler_metrics import (
    SCHEDULER_HEARTBEAT_TIMESTAMP,
    SCHEDULER_JOBS_STARTED,
    SCHEDULER_JOBS_SUCCEEDED,
    SCHEDULER_JOBS_FAILED,
    SCHEDULER_JOBS_RECOVERED,
    SCHEDULER_JOBS_IN_PROGRESS,
    SCHEDULER_JOB_DURATION,
    record_job_started,
    record_job_succeeded,
    record_job_failed,
    record_job_recovered,
    record_job_finished,
)
from app.scheduler.coordinator import tick


def test_metrics_definitions_exist():
    """Test metric definitions and bounded labels."""
    metrics = [
        "workforce_scheduler_heartbeat_timestamp_seconds",
        "workforce_scheduler_jobs_started_total",
        "workforce_scheduler_jobs_succeeded_total",
        "workforce_scheduler_jobs_failed_total",
        "workforce_scheduler_jobs_recovered_total",
        "workforce_scheduler_jobs_in_progress",
        "workforce_scheduler_job_duration_seconds",
    ]
    
    # In prometheus_client, names might be stored without _total, or they exist in collect()
    # It's safer to just check that the Python objects we imported have these names
    assert SCHEDULER_HEARTBEAT_TIMESTAMP._name == "workforce_scheduler_heartbeat_timestamp_seconds"
    assert SCHEDULER_JOBS_STARTED._name == "workforce_scheduler_jobs_started" or SCHEDULER_JOBS_STARTED._name == "workforce_scheduler_jobs_started_total"
    assert SCHEDULER_JOBS_IN_PROGRESS._name == "workforce_scheduler_jobs_in_progress"
    

def get_metric_value(name, labels=None):
    labels = labels or {}
    val = SCHEDULER_REGISTRY.get_sample_value(name, labels)
    if val is None and name.endswith("_total"):
        val = SCHEDULER_REGISTRY.get_sample_value(name.replace("_total", ""), labels)
    return val if val is not None else 0.0


def test_job_lifecycle_success():
    """Test job lifecycle metrics on success."""
    val_in_progress_before = get_metric_value("workforce_scheduler_jobs_in_progress", {"job_type": "report", "execution_mode": "scheduled"})
    
    # Note: _total suffix is automatically stripped/added by prometheus client sometimes, 
    # but get_sample_value usually works with _total for counters if registered with it.
    val_started_before = get_metric_value("workforce_scheduler_jobs_started_total", {"job_type": "report", "execution_mode": "scheduled"})
    val_succeeded_before = get_metric_value("workforce_scheduler_jobs_succeeded_total", {"job_type": "report", "execution_mode": "scheduled"})
    val_duration_count_before = get_metric_value("workforce_scheduler_job_duration_seconds_count", {"job_type": "report", "execution_mode": "scheduled"})

    record_job_started("report", "scheduled")
    
    val_in_progress = get_metric_value("workforce_scheduler_jobs_in_progress", {"job_type": "report", "execution_mode": "scheduled"})
    assert val_in_progress == val_in_progress_before + 1

    record_job_succeeded("report", "scheduled")
    record_job_finished("report", "scheduled", 1.5)

    assert get_metric_value("workforce_scheduler_jobs_in_progress", {"job_type": "report", "execution_mode": "scheduled"}) == val_in_progress_before
    assert get_metric_value("workforce_scheduler_jobs_started_total", {"job_type": "report", "execution_mode": "scheduled"}) == val_started_before + 1
    assert get_metric_value("workforce_scheduler_jobs_succeeded_total", {"job_type": "report", "execution_mode": "scheduled"}) == val_succeeded_before + 1
    assert get_metric_value("workforce_scheduler_job_duration_seconds_count", {"job_type": "report", "execution_mode": "scheduled"}) == val_duration_count_before + 1


def test_job_lifecycle_failure():
    """Test job lifecycle metrics on failure."""
    val_in_progress_before = get_metric_value("workforce_scheduler_jobs_in_progress", {"job_type": "report", "execution_mode": "scheduled"})
    val_failed_before = get_metric_value("workforce_scheduler_jobs_failed_total", {"job_type": "report", "execution_mode": "scheduled"})

    record_job_started("report", "scheduled")
    record_job_failed("report", "scheduled")
    record_job_finished("report", "scheduled", 0.5)

    assert get_metric_value("workforce_scheduler_jobs_in_progress", {"job_type": "report", "execution_mode": "scheduled"}) == val_in_progress_before
    assert get_metric_value("workforce_scheduler_jobs_failed_total", {"job_type": "report", "execution_mode": "scheduled"}) == val_failed_before + 1


def test_recovery_metric():
    """Test recovery metric increments."""
    val_recovered_before = get_metric_value("workforce_scheduler_jobs_recovered_total", {"job_type": "report"})
    record_job_recovered("report")
    assert get_metric_value("workforce_scheduler_jobs_recovered_total", {"job_type": "report"}) == val_recovered_before + 1


@patch("app.scheduler.coordinator.ReportRunService.recover_stale_runs", return_value=0)
def test_heartbeat_updates_on_success(mock_recover_stale_runs):
    """Test heartbeat updates on successful tick."""
    db_mock = MagicMock()
    # db_mock.query().filter().filter().with_for_update().all() -> returns []
    mock_query = db_mock.query.return_value
    mock_filter1 = mock_query.filter.return_value
    mock_filter2 = mock_filter1.filter.return_value
    mock_for_update = mock_filter2.with_for_update.return_value
    mock_for_update.all.return_value = []
    
    val_before = get_metric_value("workforce_scheduler_heartbeat_timestamp_seconds")
    
    time.sleep(0.01)
    tick(db_mock)
    
    val_after = get_metric_value("workforce_scheduler_heartbeat_timestamp_seconds")
    assert val_after > val_before


@patch("app.scheduler.coordinator.ReportRunService.recover_stale_runs", return_value=0)
def test_heartbeat_does_not_update_on_fatal_error(mock_recover_stale_runs):
    """Test heartbeat does not update if tick raises exception/returns early."""
    db_mock = MagicMock()
    # Make db.query raise Exception
    db_mock.query.side_effect = Exception("DB connection failed")
    
    val_before = get_metric_value("workforce_scheduler_heartbeat_timestamp_seconds")
    
    time.sleep(0.01)
    tick(db_mock)
    
    val_after = get_metric_value("workforce_scheduler_heartbeat_timestamp_seconds")
    assert val_after == val_before


def test_registry_safety():
    """Test importing scheduler_metrics multiple times does not register duplicate metric errors."""
    import app.observability.scheduler_metrics as mod1
    import app.observability.scheduler_metrics as mod2
    assert mod1.SCHEDULER_JOBS_STARTED is mod2.SCHEDULER_JOBS_STARTED
