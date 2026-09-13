import os
from pathlib import Path

def get_audit_file():
    return Path(__file__).parent.parent / "docs" / "scheduler-observability-audit.md"

def test_scheduler_observability_audit_exists():
    """Verify the audit document was created."""
    audit_file = get_audit_file()
    assert audit_file.exists(), "Audit document must exist"

def test_scheduler_heartbeat_strategy_is_documented():
    """Verify heartbeat strategy is documented."""
    content = get_audit_file().read_text()
    assert "workforce_scheduler_heartbeat_timestamp_seconds" in content
    assert "Gauge" in content or "timestamp" in content.lower()

def test_scheduler_metrics_avoid_unbounded_identifiers():
    """Verify cardinality risks are documented."""
    content = get_audit_file().read_text()
    assert "report_id" in content
    assert "user_id" in content
    assert "Prohibited" in content or "prohibited" in content.lower()
    
def test_success_and_failure_metrics_are_distinguished():
    """Verify the audit recommends separate success/failure counters."""
    content = get_audit_file().read_text()
    assert "workforce_scheduler_jobs_succeeded_total" in content
    assert "workforce_scheduler_jobs_failed_total" in content

def test_stale_recovery_is_observable():
    """Verify stale recovery metrics are recommended."""
    content = get_audit_file().read_text()
    assert "workforce_scheduler_jobs_recovered_total" in content
