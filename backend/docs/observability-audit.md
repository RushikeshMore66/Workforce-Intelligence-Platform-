# Observability Architecture Audit

## 1. Executive Summary
This document audits the existing observability state of the Workforce Intelligence Platform backend. The audit inspects application logging, exception handling, request correlation, HTTP timing, scheduler observability, database observability, and dependency usage. It concludes with a target architecture to introduce request IDs, structured logging, and metrics without disrupting existing workflows.

## 2. Current Logging Architecture
| Area | Current implementation | Risk | Recommendation |
| --- | --- | --- | --- |
| Application logging | Python's standard `logging` module is used. Not centrally configured. | Inconsistent log formatting; lack of JSON structuring. | Configure standard `logging` centrally with a custom JSON formatter. |
| Exception logging | Handled globally in `main.py` via `logger.exception()` for 500s. | Tracebacks are preserved, but not structured. | Use structured exception logging to allow querying by trace signature. |
| Scheduler logging | `worker.py`, `scheduler.py`, `jobs.py`, and `coordinator.py` use `logger.info()`/`logger.warning()`. | Operator relies solely on stdout for worker liveness. | Emit structured logs with job IDs. |
| Database logging | SQLAlchemy `echo=settings.DEBUG` is supported in `database.py`. | High verbosity in development; risk of leaking sensitive data if enabled in production. | Ensure `echo=False` in production; log only slow queries or pool events. |
| Uvicorn logging | Default Uvicorn loggers are used. | Uvicorn access logs are separated from application context. | Override Uvicorn log config to use the application's central JSON formatter. |

## 3. Exception and Error Logging
Exceptions are converted to standard HTTP responses in `app/main.py` using exception handlers. 
Unhandled exceptions are caught by the `Exception` handler, which logs the full traceback using `logger.exception` and returns a generic 500 response. This prevents leaking stack traces to clients while keeping errors visible in the server logs. 
However, error events are currently unstructured text.

## 4. Request Correlation
**Gap Identified:** There is currently no `X-Request-ID` middleware, nor is `contextvars` utilized to propagate a request ID through asynchronous application code.
A request cannot be seamlessly followed from HTTP router -> Service -> Database -> Scheduler. 

**Recommendation:** Introduce request correlation using standard library `contextvars` populated by a minimal FastAPI middleware.

## 5. HTTP Timing
**Gap Identified:** Request duration is not currently measured. There are no uses of `time.perf_counter()` for latency tracking and no response middleware timing requests.

**Recommendation:** Exclude health endpoints and `/metrics` from standard timing, and use bounded route-template labels for metrics to avoid high cardinality.

## 6. Scheduler Observability
- **Scheduler heartbeat:** There is no explicit heartbeat metric, only periodic tick logs.
- **Last successful execution:** Recorded in the database (`schedule.last_run_at`).
- **Failed/stale runs logged:** `report_execution_service.py` logs failed executions with `logger.exception()`. `coordinator.py` logs stale run recovery.
- **Process liveness:** Operators currently have to monitor the worker stdout. There is no HTTP `/health` or readiness probe for the standalone worker process.
- **Execution durations:** Report execution duration is not explicitly timed or logged.
- **Job types:** There is a clear database-level distinction between scheduled, manual, and failed executions.

## 7. Database Observability
- **Connection failures:** Bubble up to the global exception handler in `main.py` (which logs an unhandled exception).
- **Transaction rollbacks:** Handled in `get_db()` via `db.rollback()`, but the rollback event itself is not logged—it just re-raises the exception.
- **Slow queries / Pool exhaustion:** Not currently measurable.
- **Readiness check:** `app/routers/health.py` explicitly checks DB connectivity and logs failures.

## 8. Existing Dependencies
The `requirements.txt` file does not contain any observability-specific packages such as:
- `prometheus_client`
- `prometheus-fastapi-instrumentator`
- `opentelemetry`
- `structlog`
- `python-json-logger`
- `sentry_sdk`

## 9. Security and Privacy Risks
While standard exception logging in `main.py` masks details from HTTP clients, full tracebacks are emitted to stdout. If a request validation error or internal error contains PII or sensitive tokens, it may be recorded in plain text.
Database logging with `echo=True` must not be enabled in production.

## 10. Recommended Target Architecture
```text
                    ┌─────────────────────┐
                    │    HTTP Request     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Request ID Middleware│
                    │ ContextVar Binding   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       ┌────────────┐  ┌─────────────┐  ┌──────────────┐
       │ Structured │  │ HTTP Metrics │  │ Error Events │
       │ Logging    │  │ Middleware   │  │              │
       └─────┬──────┘  └──────┬──────┘  └──────────────┘
             │                │
             └────────┬───────┘
                      ▼
              ┌───────────────┐
              │ Router/Service│
              └───────┬───────┘
                      │
             ┌────────┴────────┐
             ▼                 ▼
      ┌─────────────┐   ┌──────────────┐
      │ PostgreSQL  │   │ Report Worker│
      │ Metrics     │   │ Metrics      │
      └─────────────┘   └──────────────┘
```

## 11. Implementation Plan
Phase 7.21.5.2 will focus on:
1. Creating the Request ID Middleware.
2. Integrating standard library `contextvars` to propagate the ID.

Subsequent phases will incrementally introduce structured logging, prometheus metrics, and error tracking points.

## Request ID Middleware Implementation

### Header
X-Request-ID

### Behavior
- Reuses valid incoming request IDs.
- Generates UUIDs when missing or invalid.
- Stores IDs in a ContextVar.
- Returns the ID in every response.
- Resets context after request completion.

### Security
Incoming request IDs are validated and length-limited.
Control characters are rejected.
Request IDs are used only for correlation.

## Structured Logging Implementation

### Logging Library
Python standard logging.

### Output Format
JSON lines written to stdout/stderr.

### Context Fields
- timestamp
- level
- logger
- environment
- service
- request_id
- message

### Request Correlation
The request ID is read from the ContextVar implemented by Request ID Middleware.

### Security
Sensitive credentials, tokens, passwords, and connection strings must never be logged.

Logs should be collected externally by the hosting platform, Docker logging driver, or log aggregation service rather than written to a shared application file.

## Prometheus Metrics Implementation

### Metrics
- workforce_http_requests_total
- workforce_http_request_duration_seconds
- workforce_http_requests_in_progress

### Labels
Only bounded labels are permitted:
- method
- route template
- status code

Raw URLs, user IDs, request IDs, query parameters, and exception messages are prohibited.

### Endpoint
GET /metrics

### Security
The metrics endpoint must be restricted to internal monitoring infrastructure.

## 12. Acceptance Criteria
All goals for the audit phase have been met: gaps documented, architecture defined, and architectural tests established without altering the production runtime.
