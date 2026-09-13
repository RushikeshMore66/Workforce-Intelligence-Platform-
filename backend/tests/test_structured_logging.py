import json
import logging
import sys

from app.observability.logging import JSONFormatter, RequestIDFilter, configure_logging
from app.observability.request_context import get_request_id, request_id_context


def test_formatter_produces_valid_json():
    """Test 1 — Formatter Produces Valid JSON"""
    formatter = JSONFormatter()
    record = logging.LogRecord("test", logging.INFO, "pathname", 1, "hello", (), None)

    formatted = formatter.format(record)
    payload = json.loads(formatted)

    assert payload["level"] == "INFO"
    assert payload["logger"] == "test"
    assert payload["message"] == "hello"


def test_request_id_is_automatically_included():
    """Test 2 — Request ID Is Automatically Included"""
    token = request_id_context.set("test-request-123")
    try:
        formatter = JSONFormatter()
        record = logging.LogRecord(
            "test", logging.INFO, "pathname", 1, "hello", (), None
        )
        f = RequestIDFilter()
        f.filter(record)
        formatted = formatter.format(record)
        payload = json.loads(formatted)
        assert payload["request_id"] == "test-request-123"
    finally:
        request_id_context.reset(token)


def test_missing_request_id_uses_safe_default():
    """Test 3 — Missing Request ID Uses Safe Default"""
    assert get_request_id() == "-"
    formatter = JSONFormatter()
    record = logging.LogRecord("test", logging.INFO, "pathname", 1, "hello", (), None)
    f = RequestIDFilter()
    f.filter(record)
    formatted = formatter.format(record)
    payload = json.loads(formatted)
    assert payload["request_id"] == "-"


def test_environment_and_service_are_included():
    """Test 4 — Environment and Service Are Included"""
    formatter = JSONFormatter()
    record = logging.LogRecord("test", logging.INFO, "pathname", 1, "hello", (), None)
    formatted = formatter.format(record)
    payload = json.loads(formatted)
    assert "environment" in payload
    assert payload["service"] == "workforce-api"
    
    record_scheduler = logging.LogRecord("workforce_scheduler", logging.INFO, "pathname", 1, "hello", (), None)
    formatted_scheduler = formatter.format(record_scheduler)
    payload_scheduler = json.loads(formatted_scheduler)
    assert payload_scheduler["service"] == "workforce-scheduler"


def test_exception_traceback_is_preserved():
    """Test 5 — Exception Traceback Is Preserved"""
    try:
        1 / 0
    except ZeroDivisionError as e:
        exc_info = sys.exc_info()

    formatter = JSONFormatter()
    record = logging.LogRecord(
        "test", logging.ERROR, "pathname", 1, "Something failed", (), exc_info
    )
    formatted = formatter.format(record)
    payload = json.loads(formatted)

    assert payload["exception_type"] == "ZeroDivisionError"
    assert "Traceback (most recent call last):" in payload["traceback"]
    assert "division by zero" in payload["traceback"]


def test_sensitive_values_are_not_automatically_included():
    """Test 6 — Sensitive Values Are Not Automatically Included"""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        "test", logging.INFO, "pathname", 1, "Safe message", (), None
    )
    formatted = formatter.format(record)

    assert "SECRET_KEY" not in formatted
    assert "DATABASE_URL" not in formatted


def test_logging_configuration_is_idempotent():
    """Test 7 — Logging Configuration Is Idempotent"""
    configure_logging()

    root_logger = logging.getLogger()
    handler_count = len(root_logger.handlers)

    configure_logging()

    assert len(root_logger.handlers) == handler_count


def test_existing_application_logger_works():
    """Test 8 — Existing Application Logger Works"""
    configure_logging()
    logger = logging.getLogger("app.services.example")

    assert any(
        isinstance(h.formatter, JSONFormatter) for h in logging.getLogger().handlers
    )
