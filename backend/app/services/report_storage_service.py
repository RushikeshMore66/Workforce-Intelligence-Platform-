import os
import re
from datetime import datetime, timezone
from pathlib import Path


class ReportStorageService:
    def __init__(self, storage_root: str | Path):
        self.storage_root = Path(storage_root).resolve()

    def write(
        self,
        content: bytes,
        report_type: str,
        schedule_id: str,
        scheduled_for: datetime | None,
        fmt: str,
    ) -> tuple[Path, str]:
        """
        Stores a report file securely and returns the absolute path and filename.
        """
        safe_type = self._sanitize(report_type)
        safe_schedule_id = self._sanitize(schedule_id)
        safe_fmt = self._sanitize(fmt)

        if scheduled_for:
            ts = scheduled_for.astimezone(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
        else:
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

        filename = f"{safe_type}_{ts}.{safe_fmt}"

        dest_dir = self.storage_root / safe_type / safe_schedule_id
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_path = dest_dir / filename
        dest_path.write_bytes(content)

        return dest_path, filename

    def resolve_safe(self, path: str | Path) -> Path:
        """
        Resolves the given path and ensures it does not escape the storage root.
        """
        resolved = Path(path).resolve()

        try:
            resolved.relative_to(self.storage_root)
        except ValueError:
            raise ValueError("Path traversal detected or path outside storage root")

        return resolved

    def _sanitize(self, val: str) -> str:
        """
        Strips null bytes and replaces non-alphanumeric chars (except - and _) with _.
        """
        val = val.replace("\x00", "")
        if not val:
            val = "unknown"
        return re.sub(r"[^a-zA-Z0-9_-]", "_", val)
