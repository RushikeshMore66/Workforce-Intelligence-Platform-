from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from app.models.report_schedule import ReportFrequencyEnum


def calculate_next_run_at(
    current_next_run_at: datetime,
    frequency: ReportFrequencyEnum,
    now_utc: datetime,
) -> datetime:
    """
    Calculate the next scheduled run time.
    Always advances at least once.
    Advances into the future if the schedule is significantly overdue.
    Preserves the original timezone awareness.
    """
    if current_next_run_at.tzinfo is None:
        raise ValueError("current_next_run_at must be timezone-aware")
    if now_utc.tzinfo is None:
        raise ValueError("now_utc must be timezone-aware")

    if frequency == ReportFrequencyEnum.DAILY:
        delta = timedelta(days=1)
    elif frequency == ReportFrequencyEnum.WEEKLY:
        delta = timedelta(weeks=1)
    elif frequency == ReportFrequencyEnum.MONTHLY:
        delta = relativedelta(months=1)
    else:
        raise ValueError(f"Unknown frequency: {frequency}")

    next_dt = current_next_run_at + delta

    while next_dt <= now_utc:
        next_dt = next_dt + delta

    return next_dt
