"""Schemas for report export endpoints."""

from app.schemas.common import BaseSchema


class ExportFormatError(Exception):
    """Raised when an unsupported export format is requested."""
    pass
