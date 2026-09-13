# Monitoring Documentation

## Scraping /metrics
The application exposes Prometheus metrics at the `GET /metrics` endpoint. Prometheus servers should be configured to scrape this endpoint periodically (e.g., every 15s).

## Available Metrics and Labels
### Metrics
- `workforce_http_requests_total` (Counter): Total number of HTTP requests.
- `workforce_http_request_duration_seconds` (Histogram): HTTP request duration in seconds.
- `workforce_http_requests_in_progress` (Gauge): Number of HTTP requests currently being processed.

### Labels
The application provides the following bounded labels:
- `method`: HTTP method (e.g., GET, POST).
- `route`: The matched route template (e.g., `/api/v1/projects/{project_id}`) or `<unmatched>`.
- `status`: The HTTP status code of the response.

### Why Raw Paths are Prohibited
Raw request paths (e.g., `/projects/12345`) are never used as labels because an attacker could send requests to infinite unique paths, leading to metric cardinality explosion and potentially crashing the monitoring infrastructure.

## Disabling Metrics
Metrics can be disabled via the environment variable:
```
METRICS_ENABLED=false
```
When disabled, the `/metrics` endpoint will safely return a `404 Not Found`.

## Security
The `/metrics` endpoint reveals detailed route inventory, traffic volume, and error rates. It should **not** be publicly accessible.

**Deployment Recommendation:** 
Restrict access to `/metrics` at the reverse proxy/firewall level, or expose it only on an internal monitoring network.

## Multi-Worker Deployments
With multiple Uvicorn workers, an in-process Prometheus registry does not automatically aggregate metrics across workers.

**Recommendation:**
- Run exactly one API worker process per container/instance.
- Have Prometheus scrape each container/instance separately.
- Allow Prometheus to perform the aggregation.

## Scheduler Metrics
The report scheduler component exposes its own Prometheus metrics.
When `SCHEDULER_METRICS_ENABLED=true` is set, the standalone scheduler worker will start a dedicated metrics HTTP server on the port defined by `SCHEDULER_METRICS_PORT` (default 9101).

### Metrics
- `workforce_scheduler_heartbeat_timestamp_seconds` (Gauge): Unix timestamp of the last successfully completed scheduler coordination cycle.
- `workforce_scheduler_jobs_started_total` (Counter): Number of scheduler jobs started.
- `workforce_scheduler_jobs_succeeded_total` (Counter): Number of scheduler jobs completed successfully.
- `workforce_scheduler_jobs_failed_total` (Counter): Number of scheduler jobs that failed.
- `workforce_scheduler_jobs_recovered_total` (Counter): Number of stale scheduler jobs recovered.
- `workforce_scheduler_jobs_in_progress` (Gauge): Number of scheduler jobs currently executing.
- `workforce_scheduler_job_duration_seconds` (Histogram): Duration of scheduler job execution in seconds.

### Labels
Scheduler metrics use the following bounded labels:
- `job_type`: E.g., `report`.
- `execution_mode`: E.g., `scheduled`, `manual`.

### Architecture Note: Separate Registries

Scheduler metrics are intentionally exposed separately from API metrics because the scheduler is a separate long-running process. Using a dedicated `SCHEDULER_REGISTRY` running on its own port ensures process isolation and prevents accidental leakage of HTTP metrics into the scheduler process's registry.

### Local Verification Commands

Use exact metric filtering rather than relying only on visual inspection. Note that Counters and Histograms expose suffixes such as `_total`, `_count`, `_sum`, and bucket series.

For API metrics:
```bash
curl http://localhost:8000/metrics | findstr workforce_http
```

For scheduler metrics:
```bash
curl http://localhost:9101/metrics | findstr workforce_scheduler
```

### Example Prometheus Scrape Configuration

Prometheus should scrape the API and the scheduler separately since they expose metrics on different ports.

```yaml
scrape_configs:
  - job_name: workforce-api
    metrics_path: /metrics
    static_configs:
      - targets:
          - api:8000

  - job_name: workforce-scheduler
    metrics_path: /metrics
    static_configs:
      - targets:
          - scheduler:9101
```

### Recommended Alerts
```yaml
- alert: SchedulerNotTicking
  expr: time() - workforce_scheduler_heartbeat_timestamp_seconds > 120
  labels:
    severity: critical
  annotations:
    summary: "Scheduler has not completed a coordination cycle in >2 minutes."
```
