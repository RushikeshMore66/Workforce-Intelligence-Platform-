import logging
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.report_schedule import ReportSchedule
from app.services.report_execution_service import ReportExecutionService
from app.services.report_run_service import ReportRunService

logger = logging.getLogger(__name__)

def tick(db: Session) -> None:
    """
    Coordinates finding due schedules and safely executing them, and recovers stale runs.
    """
    # Phase A — Recover stale runs
    try:
        recovered = ReportRunService.recover_stale_runs(
            db,
            settings.REPORT_STALE_RUN_TIMEOUT_MINUTES,
        )
        if recovered > 0:
            logger.warning("Recovered %d stale run(s)", recovered)
    except Exception:
        db.rollback()
        logger.exception("Failed to recover stale runs")

    # Phase B — Find and execute due schedules
    now_utc = datetime.now(timezone.utc)

    try:
        # PostgreSQL-compatible locking query. 
        # SQLite does not fully support SELECT FOR UPDATE SKIP LOCKED, but this is 
        # production behavior required by the architecture.
        due_schedules = (
            db.query(ReportSchedule)
            .filter(ReportSchedule.is_active == True)
            .filter(ReportSchedule.next_run_at <= now_utc)
            .with_for_update(skip_locked=True)
            .all()
        )
    except Exception:
        db.rollback()
        logger.exception("Failed to fetch due schedules")
        return

    execution_service = ReportExecutionService(db)

    for schedule in due_schedules:
        try:
            execution_service.execute_scheduled(schedule)
        except IntegrityError:
            db.rollback()
            logger.info(
                "Duplicate scheduled execution skipped for schedule %s",
                schedule.id,
            )
        except Exception:
            db.rollback()
            logger.exception(
                "Coordinator error for schedule %s",
                schedule.id,
            )
