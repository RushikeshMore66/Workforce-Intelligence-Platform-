import time
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

SCHEDULER_REGISTRY = CollectorRegistry()

SCHEDULER_HEARTBEAT_TIMESTAMP = Gauge(
    "workforce_scheduler_heartbeat_timestamp_seconds",
    "Unix timestamp of the last successfully completed scheduler coordination cycle.",
    registry=SCHEDULER_REGISTRY,
)

SCHEDULER_JOBS_STARTED = Counter(
    "workforce_scheduler_jobs_started_total",
    "Number of scheduler jobs started.",
    ["job_type", "execution_mode"],
    registry=SCHEDULER_REGISTRY,
)

SCHEDULER_JOBS_SUCCEEDED = Counter(
    "workforce_scheduler_jobs_succeeded_total",
    "Number of scheduler jobs completed successfully.",
    ["job_type", "execution_mode"],
    registry=SCHEDULER_REGISTRY,
)

SCHEDULER_JOBS_FAILED = Counter(
    "workforce_scheduler_jobs_failed_total",
    "Number of scheduler jobs that failed.",
    ["job_type", "execution_mode"],
    registry=SCHEDULER_REGISTRY,
)

SCHEDULER_JOBS_RECOVERED = Counter(
    "workforce_scheduler_jobs_recovered_total",
    "Number of stale scheduler jobs recovered.",
    ["job_type"],
    registry=SCHEDULER_REGISTRY,
)

SCHEDULER_JOBS_IN_PROGRESS = Gauge(
    "workforce_scheduler_jobs_in_progress",
    "Number of scheduler jobs currently executing.",
    ["job_type", "execution_mode"],
    registry=SCHEDULER_REGISTRY,
)

SCHEDULER_JOB_DURATION = Histogram(
    "workforce_scheduler_job_duration_seconds",
    "Duration of scheduler job execution in seconds.",
    ["job_type", "execution_mode"],
    registry=SCHEDULER_REGISTRY,
)


def record_job_started(job_type: str, execution_mode: str) -> None:
    SCHEDULER_JOBS_STARTED.labels(job_type=job_type, execution_mode=execution_mode).inc()
    SCHEDULER_JOBS_IN_PROGRESS.labels(job_type=job_type, execution_mode=execution_mode).inc()

def record_job_succeeded(job_type: str, execution_mode: str) -> None:
    SCHEDULER_JOBS_SUCCEEDED.labels(job_type=job_type, execution_mode=execution_mode).inc()
    SCHEDULER_JOBS_IN_PROGRESS.labels(job_type=job_type, execution_mode=execution_mode).dec()

def record_job_failed(job_type: str, execution_mode: str) -> None:
    SCHEDULER_JOBS_FAILED.labels(job_type=job_type, execution_mode=execution_mode).inc()
    SCHEDULER_JOBS_IN_PROGRESS.labels(job_type=job_type, execution_mode=execution_mode).dec()

def record_job_recovered(job_type: str) -> None:
    SCHEDULER_JOBS_RECOVERED.labels(job_type=job_type).inc()

def record_job_finished(job_type: str, execution_mode: str, duration_seconds: float) -> None:
    SCHEDULER_JOB_DURATION.labels(job_type=job_type, execution_mode=execution_mode).observe(duration_seconds)
