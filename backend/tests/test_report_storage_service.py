import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.services.report_storage_service import ReportStorageService


def test_directory_creation_and_file_writing(tmp_path: Path):
    svc = ReportStorageService(tmp_path)
    content = b"test file content"
    dt = datetime(2026, 9, 4, 15, 30, tzinfo=timezone.utc)
    
    path, filename = svc.write(content, "organization", "sched_123", dt, "xlsx")
    
    assert filename == "organization_2026-09-04T15-30-00.xlsx"
    assert path.exists()
    assert path.read_bytes() == b"test file content"
    assert path.parent.name == "sched_123"
    assert path.parent.parent.name == "organization"


def test_filename_sanitization(tmp_path: Path):
    svc = ReportStorageService(tmp_path)
    content = b"test"
    dt = datetime(2026, 9, 4, 15, 30, tzinfo=timezone.utc)
    
    # Path traversal and injection attempts in names
    path, filename = svc.write(
        content,
        report_type="org/../type",
        schedule_id="sched\\123\x00",
        scheduled_for=dt,
        fmt="csv"
    )
    
    assert filename == "org____type_2026-09-04T15-30-00.csv"
    assert path.parent.name == "sched_123"
    assert path.parent.parent.name == "org____type"


def test_empty_or_invalid_report_type(tmp_path: Path):
    svc = ReportStorageService(tmp_path)
    content = b"test"
    dt = datetime(2026, 9, 4, 15, 30, tzinfo=timezone.utc)
    
    path, filename = svc.write(content, "", "", dt, "csv")
    
    assert filename == "unknown_2026-09-04T15-30-00.csv"
    assert path.parent.name == "unknown"


def test_resolve_safe_success(tmp_path: Path):
    svc = ReportStorageService(tmp_path)
    dt = datetime(2026, 9, 4, 15, 30, tzinfo=timezone.utc)
    path, filename = svc.write(b"data", "org", "sid", dt, "csv")
    
    resolved = svc.resolve_safe(path)
    assert resolved == path
    
    # Also valid as string
    resolved_str = svc.resolve_safe(str(path))
    assert resolved_str == path


def test_resolve_safe_path_traversal(tmp_path: Path):
    svc = ReportStorageService(tmp_path)
    
    # Outside the temporary root
    outside_path = tmp_path.parent / "secret.txt"
    with pytest.raises(ValueError, match="Path traversal detected"):
        svc.resolve_safe(outside_path)
        
    with pytest.raises(ValueError, match="Path traversal detected"):
        svc.resolve_safe("../../secret.txt")
        
    with pytest.raises(ValueError, match="Path traversal detected"):
        # Absolute path on Windows usually looks like C:\...
        svc.resolve_safe("C:\\Windows\\System32\\file.txt")
        
    with pytest.raises(ValueError, match="Path traversal detected"):
        svc.resolve_safe("/tmp/outside.txt")
