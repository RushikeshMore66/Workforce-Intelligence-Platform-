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
