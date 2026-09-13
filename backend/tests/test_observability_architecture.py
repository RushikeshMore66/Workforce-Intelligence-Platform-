import os
from pathlib import Path


def test_observability_audit_document_exists():
    """Verify that the observability audit document was created."""
    docs_dir = Path(__file__).parent.parent / "docs"
    audit_file = docs_dir / "observability-audit.md"
    assert audit_file.exists(), "observability-audit.md should exist"


def test_logging_dependency_inventory_is_documented():
    """Verify that the observability audit mentions the lack of structured logging dependencies."""
    docs_dir = Path(__file__).parent.parent / "docs"
    audit_file = docs_dir / "observability-audit.md"
    content = audit_file.read_text(encoding="utf-8")
    assert "structlog" in content or "python-json-logger" in content
    assert "Dependencies" in content


def test_request_id_strategy_is_documented():
    """Verify that the request ID strategy via contextvars is documented."""
    docs_dir = Path(__file__).parent.parent / "docs"
    audit_file = docs_dir / "observability-audit.md"
    content = audit_file.read_text(encoding="utf-8")
    assert "contextvars" in content.lower()
    assert "request id" in content.lower() or "x-request-id" in content.lower()


def test_scheduler_observability_gaps_are_documented():
    """Verify that scheduler liveness/heartbeat gaps are documented."""
    docs_dir = Path(__file__).parent.parent / "docs"
    audit_file = docs_dir / "observability-audit.md"
    content = audit_file.read_text(encoding="utf-8")
    assert "scheduler" in content.lower()
    assert "liveness" in content.lower() or "heartbeat" in content.lower()


def test_metrics_strategy_uses_bounded_route_labels():
    """Verify that the metrics strategy explicitly mentions bounded route-template labels."""
    docs_dir = Path(__file__).parent.parent / "docs"
    audit_file = docs_dir / "observability-audit.md"
    content = audit_file.read_text(encoding="utf-8")
    assert "bounded route-template labels" in content.lower()
