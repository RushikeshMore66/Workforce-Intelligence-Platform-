import logging

from app.database import SessionLocal
from app.scheduler.coordinator import tick

logger = logging.getLogger(__name__)


def run_scheduled_reports() -> None:
    """
    Job entrypoint for the APScheduler. 
    Creates a fresh database session for this execution, runs the coordinator tick,
    and safely closes the session.
    """
    db = SessionLocal()

    try:
        tick(db)
    except Exception:
        logger.exception("Unhandled scheduler tick failure")
    finally:
        db.close()
