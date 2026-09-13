# Production Security Checklist

> Review and sign off on every item before deploying to production.

---

## Authentication

- [ ] JWT expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`) is set to an appropriate value.
  - **Recommendation**: 60 minutes or less in production. The current default of 1440 (24 h) is acceptable for development only.
- [ ] Password hashing uses bcrypt via `bcrypt.gensalt()` — no legacy passlib passthrough.
- [ ] `SECRET_KEY` is generated securely (e.g. `openssl rand -hex 32`) and is not the placeholder from `.env.example`.
- [ ] `SECRET_KEY` is at least 32 characters long. The startup validator enforces this.
- [ ] Refresh token support is planned for a future phase; short-lived access tokens mitigate risk in the interim.

---

## Authorization

- [ ] OWNER-only endpoints (`/reports/organization`, `GET /reports/organization/export`) verified.
- [ ] SUPERVISOR scope restrictions verified: supervisors see only their own projects and teams.
- [ ] TEAM_LEADER scope restrictions verified: team leaders see only their own team and its projects.
- [ ] WORKER restrictions verified: workers see only their own profile, assigned tasks, and team.
- [ ] Resource-level authorization (`authorize_project_access`, `authorize_worker_access`, `authorize_team_access`, `authorize_task_access`, `authorize_blocker_access`, `authorize_notification_ownership`) called on every mutating endpoint.

---

## Configuration

- [ ] `DEBUG=False` in production — never `True`.
- [ ] `SECRET_KEY` is not a placeholder value. The startup validator will reject empty or short keys.
- [ ] `DATABASE_URL` is configured securely. The startup validator will reject empty values.
- [ ] `BACKEND_CORS_ORIGINS` lists only trusted production frontend origins; wildcard (`*`) must not be used.
- [ ] `TRUSTED_HOST_ENABLED=True` and `TRUSTED_HOSTS=<your-domain>` are set in production to enable `TrustedHostMiddleware`.
- [ ] `RATE_LIMIT_ENABLED` flag is present. Rate-limiting enforcement is planned for a future phase; set this `True` once a backend (e.g. slowapi) is wired in.
- [ ] Secrets (`SECRET_KEY`, `DATABASE_URL`, database passwords) are stored in environment variables or a secrets manager — never committed to source control.
- [ ] `.env` file is listed in `.gitignore` (already verified).

---

## HTTP Security

- [ ] `TrustedHostMiddleware` is configured for production hostnames.
- [ ] The global `Exception` handler returns `{"success": false, "error": "Internal Server Error", "detail": "An unexpected error occurred."}` — no stack traces, no database connection strings, no secret values leak to clients.
- [ ] The `RequestValidationError` handler returns a consistent 422 envelope.
- [ ] The `StarletteHTTPException` handler normalizes all raw HTTPExceptions to the flat project envelope.
- [ ] CORS `allow_credentials=True` is combined with explicit `allow_origins` (no wildcard).

---

## File Security

- [ ] Report download endpoints stream files from the configured `REPORT_STORAGE_PATH` only.
- [ ] `REPORT_STORAGE_PATH` is validated against path traversal: no `../` sequences are accepted.
- [ ] Absolute filesystem paths are never returned in API responses.
- [ ] `output_path` in `ReportRun` records is stored relative to `REPORT_STORAGE_PATH`, not as an absolute path.

---

## Database Security

- [ ] All queries use SQLAlchemy ORM or parameterised expressions — no raw `text()` calls with user-supplied input.
- [ ] Database credentials (`DATABASE_URL`, `POSTGRES_PASSWORD`) are stored outside source control.
- [ ] Database user in production has least-privilege access (no `SUPERUSER`, no `CREATEDB`).
- [ ] Connection pool is tuned for the production worker count: adjust `pool_size` and `max_overflow` in `database.py` for PostgreSQL deployments.

---

## Scheduler Security

- [ ] In production, the scheduler runs as a **single dedicated process** (`python -m app.scheduler.worker`), not inside the API workers.
- [ ] `REPORT_SCHEDULER_ENABLED=False` in all API worker environment configs.
- [ ] Stale run recovery timeout (`REPORT_STALE_RUN_TIMEOUT_MINUTES`) is appropriate for the expected report execution duration.

---

## Future Additions (Planned)

| Feature | Phase |
|---------|-------|
| Rate limiting enforcement | Future |
| Refresh token support | Future |
| Audit log for sensitive mutations | Future |
| CSP / security response headers | Future |
