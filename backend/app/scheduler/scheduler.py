import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.scheduler.jobs import run_scheduled_reports

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler(timezone="UTC")


def start() -> None:
    """
    Start the APScheduler if not already running.
    Adds exactly one recurring job to coordinate report execution.
    """
    if _scheduler.running:
        return

    _scheduler.add_job(
        run_scheduled_reports,
        trigger=IntervalTrigger(seconds=settings.REPORT_SCHEDULER_INTERVAL_SECONDS),
        id="report_scheduler",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=30,
        coalesce=True,
    )

    _scheduler.start()
    logger.info("Report scheduler started")


def shutdown() -> None:
    """
    Shut down the scheduler cleanly, waiting for any running jobs to finish.
    """
    if _scheduler.running:
        _scheduler.shutdown(wait=True)
        logger.info("Report scheduler shut down cleanly")
