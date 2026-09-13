# Production Deployment Readiness Audit

**Phase:** 7.21.5.6
**Target Architecture:**
- Frontend: Vercel (Next.js)
- Backend API: Railway (FastAPI)
- Backend Scheduler: Railway (Background Worker)
- Database: Railway (PostgreSQL)

---

## 1. Backend Startup: PASS
**Analysis:** The production startup command `uvicorn app.main:app --host 0.0.0.0 --port $PORT` is correctly configured for containerized deployment. The application's `lifespan` handler checks `REPORT_SCHEDULER_ENABLED`, which correctly defaults to `False` in API worker processes, preventing accidental co-location of the scheduler and API in production.
- **Graceful Shutdown:** Handled natively by Uvicorn.
- **No dev-only startup behavior:** Confirmed.

## 2. Database Deployment: PASS
**Analysis:** The database uses PostgreSQL. Migrations are managed by Alembic. 
- **Migration Idempotency:** Confirmed.
- **Startup behavior:** The API does not automatically run migrations. 
- **Requirement:** Migrations must be run manually (`alembic upgrade head`) before the API/Scheduler is deployed or as a discrete release phase on Railway.

## 3. Environment Configuration: WARNING
**Analysis:**
- `SECRET_KEY`: Properly validated by Pydantic to require length >= 32 and reject weak placeholders like "change-me". (PASS)
- `DATABASE_URL`: Required field, verified to reject SQLite in production. (PASS)
- `CORS_ALLOWED_ORIGINS`: Defaults include `localhost`, but wildcard `*` is caught by validators in production. The allowed hosts should be overridden explicitly in production. (WARNING)
- **Recommendation:** Ensure Railway variables explicitly map `BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app"]`.

## 4. Scheduler Deployment: PASS
**Analysis:**
- **Command:** `python -m app.scheduler.worker`
- **Replicas:** Only 1 replica should be configured on Railway. The architecture does not currently support distributed locking, so horizontal scaling of the scheduler is prohibited.
- **Recovery:** Stale runs are recovered on worker startup. (PASS)

## 5. Report Storage: BLOCKER
**Analysis:** The application defaults to storing reports locally at `./storage/reports`.
- **Issue:** Railway provides ephemeral disks by default. A container restart will wipe generated reports.
- **Action Required:** Either attach a persistent Railway Volume to both the API and Scheduler (complex, requires shared volume), or integrate an object storage provider like AWS S3 or Cloudflare R2. Deployment cannot proceed for reports until this is solved.

## 6. CORS and Frontend Integration: PASS
**Analysis:**
- **Frontend Config:** The `package.json`, `.env.example`, and `.env.local` were audited. 
- **Secrets:** No private credentials (like `DATABASE_URL` or `JWT_SECRET_KEY`) exist in the frontend repository or are exposed with `NEXT_PUBLIC_`.
- **Configurability:** `NEXT_PUBLIC_API_URL` correctly controls the API base path.

## 7. Docker and Deployment Files: BLOCKER
**Analysis:**
- The repository does not currently contain a `Dockerfile`, `.dockerignore`, or `railway.json` for the backend.
- **Action Required:** Create a standard Python Dockerfile and `railway.json` defining the two separate services (API and worker).

## 8. Security Audit: PASS
**Analysis:**
- **JWT:** Strong keys required.
- **Endpoints:** `api/v1/health` and `/metrics` do not expose secrets. Scheduler metrics run on a completely isolated port (9101).
- **Errors:** Handled by a global flat exception envelope. Stack traces are logged, not leaked.

## 9. Deployment Smoke Tests: BLOCKER
**Analysis:**
- **Issue:** Smoke tests do not exist.
- **Action Required:** Create `tests/test_deployment_readiness.py` to validate configurations.

## 10. Documentation: WARNING
**Analysis:**
- Runbook is missing.
- **Action Required:** Create `docs/deployment-runbook.md`.
