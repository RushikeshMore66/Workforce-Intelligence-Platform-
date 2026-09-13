# Scheduler Observability Audit

## 1. Executive Summary
The scheduler utilizes APScheduler's `BackgroundScheduler` to periodically trigger a centralized coordinator via `tick(db)`. Currently, there is no operational visibility through metrics to know if the scheduler is alive, how long jobs take, or how many succeed/fail. All telemetry is limited to standard Python logging. 

## 2. Scheduler Lifecycle
- **Startup:** The scheduler is started via `app/scheduler/scheduler.py` `start()`, either integrated within the FastAPI lifecycle or via a standalone `worker.py` process.
- **Looping:** It registers a single recurring interval job (`run_scheduled_reports`) that creates a DB session and invokes `coordinator.tick()`.
- **Concurrency:** `tick()` executes sequentially within the single scheduler job instance. Schedules are fetched using `SELECT FOR UPDATE SKIP LOCKED`.
- **Shutdown:** Stops gracefully via `shutdown()`. Standalone workers capture SIGINT/SIGTERM to trigger this.

## 3. Current Heartbeat Capability
- **Current State:** **None.** There is no metric or timestamp recorded to prove the scheduler is still polling effectively.
- **Gap:** If the scheduler process hangs, encounters a silent background thread crash, or is blocked on a DB connection pool indefinitely, no alerts can be triggered natively because there is no periodic heartbeat signal.

## 4. Report Execution Lifecycle
- **Manual vs Scheduled:** Handled by `execute_manual` and `execute_scheduled`.
- **State Flow:**
  - Scheduled runs are created (`create_scheduled_run`).
  - Marked as running (`mark_running`).
  - Report generated and exported.
  - On success: `mark_completed(path, filename)`.
  - On exception: Exception caught, logged, and `mark_failed(error_msg)` is called.
- **Success Boundary:** A run is only successful once `mark_completed` executes.
- **Failure Boundary:** Any exception during generation or export triggers `mark_failed`.

## 5. Existing Failure Handling
- **Database Exceptions:** Handled explicitly via `.rollback()` in the coordinator `tick()` and execution service.
- **Silent Failures / Hangs:** Phase A of `tick()` explicitly runs a stale run recovery (`ReportRunService.recover_stale_runs`) to identify and mark runs that remain stuck in the 'running' state past the timeout interval.

## 6. Existing Metrics and Logs
- **Logs:** 
  - Standard `logging` is implemented.
  - Logs are emitted for stale recoveries, duplicate skips, and execution failures.
- **Metrics:** **None.** No Prometheus metrics exist for the scheduler or report generation execution duration.

## 7. Missing Operational Signals
- Is the scheduler actively ticking?
- How many jobs were processed?
- How many jobs failed?
- How many stale runs were recovered?
- How long does report generation take?

## 8. Recommended Metrics
We recommend adding the following Prometheus metrics:
- `workforce_scheduler_heartbeat_timestamp_seconds` (Gauge)
- `workforce_scheduler_jobs_started_total` (Counter)
- `workforce_scheduler_jobs_succeeded_total` (Counter)
- `workforce_scheduler_jobs_failed_total` (Counter)
- `workforce_scheduler_jobs_recovered_total` (Counter)
- `workforce_scheduler_jobs_in_progress` (Gauge)
- `workforce_scheduler_job_duration_seconds` (Histogram)

## 9. Recommended Heartbeat Design
A Gauge (`workforce_scheduler_heartbeat_timestamp_seconds`) should be updated to the current Unix timestamp (`time.time()`) at the **end** of a successful `tick()` cycle. This guarantees the process is fully functional and capable of accessing the database. Prometheus can alert if `time() - workforce_scheduler_heartbeat_timestamp_seconds > 120`.

## 10. Security and Cardinality Considerations
Scheduler metrics must avoid unbound or high-cardinality labels:
- **Prohibited:** `report_id`, `project_id`, `user_id`, `worker_id`, `request_id`, raw exception strings.
- **Permitted Bounded Labels:** `job_type`, `execution_mode`, `status` (e.g., `job_type="report"`, `execution_mode="scheduled"`).

## 11. Implementation Plan
1. Create `app/observability/scheduler_metrics.py` defining the Gauges, Counters, and Histograms.
2. Update `app/scheduler/coordinator.py` to record the heartbeat on successful ticks, increment stale recoveries, and track in-progress jobs.
3. Update `app/services/report_execution_service.py` to increment started, succeeded, and failed counters, and observe execution duration via a context manager or explicit timing.

## 12. Acceptance Criteria
- [x] Scheduler lifecycle is documented accurately
- [x] Scheduler startup and shutdown behavior is documented
- [x] Existing heartbeat capability is confirmed
- [x] Missing heartbeat capability is documented
- [x] Report execution lifecycle is mapped
- [x] Success and failure boundaries are identified
- [x] Stale recovery behavior is documented
- [x] Existing scheduler logs are identified
- [x] Recommended metrics are documented
- [x] Metric cardinality risks are documented
- [x] Heartbeat timestamp strategy is documented
- [x] Architecture tests pass
- [x] No scheduler production metrics are added yet
