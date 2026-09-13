# Production Deployment Runbook

This document details the recommended procedures for deploying the Workforce Intelligence Platform to a production environment.

## 1. Prerequisites

- **PostgreSQL 14+**: A dedicated PostgreSQL cluster for production data. SQLite is explicitly blocked in production.
- **Python 3.11+**: Ensure the production environment has the correct Python runtime.
- **Environment Template**: A copy of `.env.production.example` properly filled out and saved as `.env` or loaded via the deployment platform (e.g., Docker ENV, Kubernetes Secrets).

## 2. Environment Variables

The `ENVIRONMENT=production` variable activates strict validation rules on startup:
1. Rejects SQLite database URLs.
2. Rejects tokens with `ACCESS_TOKEN_EXPIRE_MINUTES > 60`.
3. Rejects known unsafe `SECRET_KEY` placeholders (e.g., `change-me`, `super-secret...`).
4. Requires the scheduler's `REPORT_STORAGE_PATH` to be a valid, writable directory.
5. Warns if `BACKEND_CORS_ORIGINS` contains a wildcard `*`.

Ensure your deployment securely injects `SECRET_KEY` and `DATABASE_URL`.

## 3. Database Setup & Running Migrations

FastAPI's deployment guidance separates application processes from schema management. **Do not** rely on application startup to create database tables (e.g. `Base.metadata.create_all()`).

Before launching application workers or after a version upgrade, manually apply the database schema via Alembic:

```bash
cd backend
alembic upgrade head
```

This ensures a single, deterministic schema upgrade rather than multiple application workers racing to apply migrations concurrently.

## 4. Starting the API Workers

Launch the FastAPI application using Uvicorn (or Gunicorn + Uvicorn workers). The API processes handle all incoming HTTP traffic.

```bash
cd backend
# Run with a single Uvicorn process (or configure Gunicorn for multiple workers)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> **Important**: API workers must run with `REPORT_SCHEDULER_ENABLED=false` to prevent them from executing scheduled background jobs.

## 5. Starting the Scheduler Worker

The system requires exactly one dedicated worker to coordinate and execute scheduled background reports. This prevents duplicate executions and unloads heavy report generation from API workers.

```bash
cd backend
# Ensure REPORT_SCHEDULER_ENABLED=true for this process
python -m app.scheduler.worker
```

Ensure both the API and the Scheduler worker share the same `DATABASE_URL` and `REPORT_STORAGE_PATH`.

## 6. Health Checks

The application provides dedicated endpoints for load balancers and container orchestrators:

- **Liveness Probe**: `GET /api/v1/health/live`
  - Validates that the HTTP process is accepting connections. Does not query the database.
  - Expected: `200 OK` `{"status": "ok"}`
- **Readiness Probe**: `GET /api/v1/health/ready`
  - Validates that the application can reach its required dependencies (e.g., PostgreSQL).
  - Expected: `200 OK` `{"status": "ready", "database": "ok"}`
  - Degraded: `503 Service Unavailable` `{"status": "degraded", "database": "error"}`

> **Note**: The legacy `GET /api/v1/health` endpoint remains available for backwards compatibility with existing frontend checks.

## 7. Security Headers

The application automatically attaches the following security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`

**HSTS (Strict-Transport-Security)**:
HSTS (`max-age=31536000; includeSubDomains`) is automatically applied *only* if the request is served over HTTPS (or forwarded via `X-Forwarded-Proto: https` from a reverse proxy). Ensure your load balancer correctly terminates TLS and forwards the appropriate headers.

## 8. Backup & Rollback Procedures

### Backups
Schedule automated, daily `pg_dump` backups for your PostgreSQL database. Ensure backups are stored securely off-site.
Additionally, back up the contents of the `REPORT_STORAGE_PATH` if historical generated reports need to be preserved outside the database.

### Rollbacks
If a deployment introduces a critical regression:
1. Revert the application code deployment to the previous stable tag.
2. If database migrations were applied, run `alembic downgrade <target_revision>`.
3. Restart all API and Scheduler workers.

## 9. Troubleshooting

- **503 on Readiness Probe**: The database connection has failed. Check `DATABASE_URL` credentials and network connectivity to the PostgreSQL cluster.
- **Reports Not Generating**: Verify the Scheduler worker is running, `REPORT_SCHEDULER_ENABLED=true` is set, and the `REPORT_STORAGE_PATH` is writable by the scheduler process.
- **CORS Errors**: Ensure the exact frontend URL (including the scheme, e.g. `https://`) is explicitly listed in `BACKEND_CORS_ORIGINS`.
