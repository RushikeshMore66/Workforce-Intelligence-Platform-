import logging
import signal
import sys
import threading

from app.scheduler.scheduler import shutdown, start

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

stop_event = threading.Event()


def handle_signal(signum, frame):
    logger.info("Received termination signal, shutting down worker...")
    stop_event.set()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    from app.config import settings
    if settings.SCHEDULER_METRICS_ENABLED:
        from prometheus_client import start_http_server
        from app.observability.scheduler_metrics import SCHEDULER_REGISTRY
        logger.info(f"Starting scheduler metrics server on {settings.SCHEDULER_METRICS_HOST}:{settings.SCHEDULER_METRICS_PORT}")
        start_http_server(settings.SCHEDULER_METRICS_PORT, addr=settings.SCHEDULER_METRICS_HOST, registry=SCHEDULER_REGISTRY)

    logger.info("Starting standalone scheduler worker...")
    start()

    try:
        # Keep process alive cleanly without a busy loop
        stop_event.wait()
    except KeyboardInterrupt:
        pass
    finally:
        shutdown()
        logger.info("Worker process exited cleanly")
