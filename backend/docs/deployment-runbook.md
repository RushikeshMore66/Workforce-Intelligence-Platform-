# Deployment Runbook

This runbook outlines the deployment steps for the Workforce Intelligence Platform using Railway (Backend) and Vercel (Frontend).

## 1. Database Provisioning
- Provision a managed PostgreSQL instance on Railway.
- Retrieve the connection URL.
- **Rule**: Do NOT execute migrations automatically on application startup.

## 2. Configure Environment Variables
- Set up all variables listed in `.env.production.example` on Railway.
- Ensure `SECRET_KEY` is a strong, unique value >= 32 characters.
- Configure `BACKEND_CORS_ORIGINS` to include the frontend production URL (e.g., `["https://workforce.yourdomain.com"]`).
- Set `REPORT_STORAGE_PATH` according to your persistent volume setup or external storage configuration.

## 3. Run Alembic Migrations
- Trigger a release command or manually run the migration script against the production database:
```bash
alembic upgrade head
```

## 4. Deploy FastAPI API
- Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Ensure `REPORT_SCHEDULER_ENABLED=false` is set for this service.
- Enable `TRUSTED_HOST_ENABLED=true` and `TRUSTED_HOSTS=...` if sitting directly behind a balancer that respects it.

## 5. Deploy Scheduler Worker
- Command: `python -m app.scheduler.worker`
- **Rule**: Deploy exactly 1 replica to avoid distributed lock issues.
- Ensure `SCHEDULER_METRICS_ENABLED=true` and `REPORT_SCHEDULER_ENABLED=true`.

## 6. Deploy Next.js Frontend
- Deploy the `src` application to Vercel.
- Configure `NEXT_PUBLIC_API_URL` to point to the deployed Railway API (e.g., `https://api-workforce.up.railway.app`).
- Command:
```bash
npm ci
npm run build
npm run start
```
- Ensure no secrets like `DATABASE_URL` or `JWT_SECRET_KEY` are configured in Vercel.

## 7. Verify Health Endpoints
- `GET /api/v1/health/live`: Process is alive. Returns a 200 OK.
- `GET /api/v1/health/ready`: Application/database is ready. Ensures the DB connection is active.
- `GET /health` or `/api/v1/health`: Basic health responses containing no secrets.
- `/metrics`: API metrics (should be protected or internal).
- `9101/metrics`: Internal scheduler metrics.

## 8. Rollback Procedure
If a deployment fails:
1. Revert the Git commit to the previous stable state and trigger a new deployment.
2. If database schema was altered, you must down-migrate carefully (e.g., `alembic downgrade -1`). Make sure down-migrations are safe and tested before running against production.
3. Verify `/api/v1/health/ready` returns 200 OK.
