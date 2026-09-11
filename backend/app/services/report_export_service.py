"""
ReportExportService — generates CSV, XLSX, and PDF exports from existing report data.

Design principles:
- Reuses ReportService to fetch data — zero duplication of metric logic.
- All generation happens in-memory (BytesIO/StringIO); no files written to disk.
- PDF uses reportlab.platypus with escaped user-controlled text.
- XLSX uses openpyxl.
- CSV uses stdlib csv module.
- Returns (bytes, content_type, filename) tuples for the router.

Supported formats: csv, xlsx, pdf (case-insensitive, rejected otherwise with HTTP 400).
"""

import csv
import io
import re
from datetime import date, datetime
from typing import Optional

from fastapi import HTTPException

from app.schemas.reports import (
    ActivityReport,
    OrganizationSummaryReport,
    ProjectPerformanceReport,
    TeamPerformanceReport,
    WorkerPerformanceReport,
)


SUPPORTED_FORMATS = {"csv", "xlsx", "pdf"}

CONTENT_TYPES = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pdf": "application/pdf",
}


def _validate_format(fmt: str) -> str:
    fmt = fmt.lower().strip()
    if fmt not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported export format '{fmt}'. Supported: csv, xlsx, pdf.",
        )
    return fmt


def _sanitize_filename(name: str) -> str:
    """Remove path separators, null bytes, and control characters."""
    name = re.sub(r"[\x00-\x1f/\\]", "_", name)
    return name[:100]


def _content_disposition(filename: str) -> str:
    return f'attachment; filename="{filename}"'


# ─── CSV ─────────────────────────────────────────────────────────────────────


def _summary_to_csv_rows(data: dict) -> list[list]:
    """Convert a flat dict of metric→value pairs to [Metric, Value] rows."""
    rows = [["Metric", "Value"]]
    for key, val in data.items():
        if key == "metadata":
            continue
        rows.append([str(key), str(val)])
    return rows


def _activity_to_csv_rows(report: ActivityReport) -> list[list]:
    header = [
        "ID", "Task ID", "Task Title", "Worker ID", "Worker Name",
        "Project ID", "Project Name", "Created By User ID", "Description",
        "Timestamp", "Authorship",
    ]
    rows = [header]
    for item in report.items:
        rows.append([
            item.update_id,
            item.task_id,
            item.task_title,
            item.worker_id,
            item.worker_name,
            item.project_id,
            item.project_name,
            item.created_by_user_id or "",
            item.description,
            item.timestamp.isoformat(),
            item.authorship,
        ])
    return rows


def build_csv(rows: list[list]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


# ─── XLSX ────────────────────────────────────────────────────────────────────


def build_xlsx(sheet_name: str, rows: list[list]) -> bytes:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter

    # Excel forbids: : / \ ? * [ ] in sheet names
    _invalid_sheet_chars = re.compile(r"[:/\\?*\[\]]")
    sheet_name = _invalid_sheet_chars.sub("_", sheet_name)[:31]

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")

    for r_idx, row in enumerate(rows, start=1):
        for c_idx, val in enumerate(row, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            if r_idx == 1:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center")

    # Auto-size columns (capped at 60)
    for col_idx in range(1, ws.max_column + 1):
        col_letter = get_column_letter(col_idx)
        max_len = max(
            (len(str(ws.cell(row=r, column=col_idx).value or "")) for r in range(1, ws.max_row + 1)),
            default=10,
        )
        ws.column_dimensions[col_letter].width = min(max_len + 4, 60)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ─── PDF ─────────────────────────────────────────────────────────────────────


def _escape_pdf(text: str) -> str:
    """Escape angle brackets and strip null bytes for ReportLab."""
    if not isinstance(text, str):
        text = str(text)
    text = text.replace("\x00", "")
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return text


def build_pdf(title: str, rows: list[list]) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    buf = io.BytesIO()
    # Use landscape for wide activity tables
    pagesize = landscape(A4) if len(rows[0]) > 5 else A4
    doc = SimpleDocTemplate(buf, pagesize=pagesize, leftMargin=1.5 * cm,
                            rightMargin=1.5 * cm, topMargin=2 * cm, bottomMargin=2 * cm)

    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(_escape_pdf(title), styles["Title"]))
    elements.append(Spacer(1, 0.5 * cm))
    # Generated timestamp
    elements.append(Paragraph(
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        styles["Normal"],
    ))
    elements.append(Spacer(1, 0.5 * cm))

    # Escape all cell content
    safe_rows = [[_escape_pdf(str(cell)) for cell in row] for row in rows]

    table_data = safe_rows
    col_count = len(table_data[0]) if table_data else 1

    # Build table
    t = Table(table_data, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t)

    doc.build(elements)
    return buf.getvalue()


# ─── Dispatcher ──────────────────────────────────────────────────────────────


class ReportExportService:
    """Builds export bytes from a pre-fetched report schema object."""

    def export_organization(
        self, report: OrganizationSummaryReport, fmt: str
    ) -> tuple[bytes, str, str]:
        fmt = _validate_format(fmt)
        raw = report.model_dump()
        rows = _summary_to_csv_rows(raw)
        title = "Organization Summary Report"
        base = _sanitize_filename("organization-report")
        filename = f"{base}.{fmt}"
        return _render(title, rows, fmt), CONTENT_TYPES[fmt], filename

    def export_project(
        self, report: ProjectPerformanceReport, fmt: str
    ) -> tuple[bytes, str, str]:
        fmt = _validate_format(fmt)
        raw = report.model_dump()
        rows = _summary_to_csv_rows(raw)
        title = f"Project Report: {report.project_name}"
        pid = _sanitize_filename(report.project_id)
        base = _sanitize_filename(f"project-{pid}-report")
        filename = f"{base}.{fmt}"
        return _render(title, rows, fmt), CONTENT_TYPES[fmt], filename

    def export_worker(
        self, report: WorkerPerformanceReport, fmt: str
    ) -> tuple[bytes, str, str]:
        fmt = _validate_format(fmt)
        raw = report.model_dump()
        rows = _summary_to_csv_rows(raw)
        title = f"Worker Report: {report.worker_name}"
        wid = _sanitize_filename(report.worker_id)
        base = _sanitize_filename(f"worker-{wid}-report")
        filename = f"{base}.{fmt}"
        return _render(title, rows, fmt), CONTENT_TYPES[fmt], filename

    def export_team(
        self, report: TeamPerformanceReport, fmt: str
    ) -> tuple[bytes, str, str]:
        fmt = _validate_format(fmt)
        raw = report.model_dump()
        rows = _summary_to_csv_rows(raw)
        title = f"Team Report: {report.team_name}"
        tid = _sanitize_filename(report.team_id)
        base = _sanitize_filename(f"team-{tid}-report")
        filename = f"{base}.{fmt}"
        return _render(title, rows, fmt), CONTENT_TYPES[fmt], filename

    def export_activity(
        self, report: ActivityReport, fmt: str
    ) -> tuple[bytes, str, str]:
        fmt = _validate_format(fmt)
        rows = _activity_to_csv_rows(report)
        title = "Activity Report"
        base = _sanitize_filename("activity-report")
        filename = f"{base}.{fmt}"
        return _render(title, rows, fmt), CONTENT_TYPES[fmt], filename


def _render(title: str, rows: list[list], fmt: str) -> bytes:
    if fmt == "csv":
        return build_csv(rows)
    elif fmt == "xlsx":
        sheet_name = title[:31]
        return build_xlsx(sheet_name, rows)
    elif fmt == "pdf":
        return build_pdf(title, rows)
    raise HTTPException(status_code=400, detail=f"Unknown format: {fmt}")
