import json
import logging
import sys
import traceback
from datetime import datetime, timezone

from app.config import settings
from app.observability.request_context import get_request_id


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Determine service name based on logger name
        service = "workforce-scheduler" if "scheduler" in record.name else "workforce-api"
        
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "environment": settings.ENVIRONMENT,
            "service": service,
            "request_id": getattr(record, "request_id", get_request_id()),
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception_type"] = record.exc_info[0].__name__ if record.exc_info[0] else "Exception"
            payload["traceback"] = "".join(traceback.format_exception(*record.exc_info))

        return json.dumps(payload)


class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = get_request_id()
        return True


_logging_configured = False

def configure_logging() -> None:
    global _logging_configured
    if _logging_configured:
        return
        
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    handler.addFilter(RequestIDFilter())
    root_logger.addHandler(handler)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(logger_name)
        uv_logger.handlers = []
        uv_logger.propagate = True

    _logging_configured = True
