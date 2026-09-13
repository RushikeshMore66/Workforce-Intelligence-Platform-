# Production Architecture Audit — Phase 7.21.1

**Audit Date**: 2026-09-12  
**Platform**: Workforce Intelligence Platform  
**Scope**: Backend architecture, dependency review, security posture, and production readiness

---

## Executive Summary

The backend is structurally sound. Authentication, RBAC, session lifecycle, database schema, and scheduler discipline are well-implemented. The main gaps requiring targeted hardening are:

| Area | Status | Action |
|------|--------|--------|
| Application startup | ✅ Strong | No change |
| Router registration | ✅ Strong | No change |
| SQLAlchemy session lifecycle | ✅ Strong | No change |
| Alembic migrations | ✅ Strong | No change |
| Environment configuration | ⚠️ Needs hardening | Added validators |
| Dependency versions | ✅ Adequate | Document |
| Authentication dependencies | ✅ Strong | Minor extension |
| Scheduler startup | ✅ Strong | No change |
| Exception handling | ⚠️ Inconsistent | Normalized |
| Logging | ❌ Not configured | Pending (7.21.5) |
| Health/readiness | ⚠️ Incomplete | Pending (7.21.6) |

---

## 1. Application Startup

**File**: [`app/main.py`](../backend/app/main.py)

The application uses FastAPI's `lifespan` async context manager for startup/shutdown hooks.

```
Startup sequence:
  1. FastAPI app is created with settings from app/config.py
  2. CORS middleware is registered
  3. [Conditional] TrustedHostMiddleware when TRUSTED_HOST_ENABLED=True
  4. Exception handlers are registered
  5. [Conditional] APScheduler starts if REPORT_SCHEDULER_ENABLED=True
  6. All routers are included with /api/v1 prefix
```

**Findings**:
- Settings validation runs at import time via Pydantic validators — startup fails fast if `SECRET_KEY` or `DATABASE_URL` are invalid. ✅
- `DEBUG=True` in the development `.env` causes SQLAlchemy to echo all queries. Must be `False` in production.
- OpenAPI docs are exposed at `/docs` and `/redoc` with no authentication. Consider disabling in production (`docs_url=None, redoc_url=None`).

---

## 2. Router Registration

**File**: [`app/routers/__init__.py`](../backend/app/routers/__init__.py)

All 12 routers are registered:

| Router | Prefix | Auth Required |
|--------|--------|--------------|
| auth | `/api/v1/auth` | No (login); Yes (me) |
| dashboard | `/api/v1/dashboard` | Yes |
| projects | `/api/v1/projects` | Yes |
| workers | `/api/v1/workers` | Yes |
| supervisors | `/api/v1/supervisors` | Yes |
| teams | `/api/v1/teams` | Yes |
| tasks | `/api/v1/tasks` | Yes |
| blockers | `/api/v1/blockers` | Yes |
| analytics | `/api/v1/analytics` | Yes |
| notifications | `/api/v1/notifications` | Yes |
| reports | `/api/v1/reports` | Yes (with RBAC) |
| report_schedules | `/api/v1/reports/schedules` | Yes (with RBAC) |

**Findings**: No unprotected routes identified beyond the login endpoint and health check. ✅

---

## 3. SQLAlchemy Session Lifecycle

**File**: [`app/database.py`](../backend/app/database.py)

```python
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,   # Validates connections before use
    echo=settings.DEBUG,  # Query logging in debug mode only
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # Prevents lazy-load after commit
)
```

The `get_db()` dependency:
- Yields one session per HTTP request.
- Rolls back on any exception — preventing partial writes from persisting.
- Closes the session in the `finally` block.

**Findings**: ✅ Correct. For PostgreSQL in production, tune `pool_size` (default 5) and `max_overflow` (default 10) based on the number of Uvicorn workers.

---

## 4. Alembic Migrations

**File**: [`migrations/env.py`](../backend/migrations/env.py)

Alembic is configured to:
- Source `DATABASE_URL` from application settings (not from `alembic.ini`).
- Import all models via `import app.models` to ensure full metadata registration.
- Use `compare_type=True` and `compare_server_default=True` for accurate autogenerate output.

**Migration history** (5 migrations):

| Revision | Description |
|----------|-------------|
| `cbe632974f17` | Initial workforce schema |
| `49c68e298daa` | Add TaskTransition |
| `987e1ddf1ae1` | Add WorkUpdate.created_by_user_id |
| `c44abb9df33c` | Report schedules |
| `e06e69fd8b2e` | Execution fields |

**Findings**: ✅ Migrations are linear with no branching. The `alembic.ini` does not store the database URL (it is injected from settings).

---

## 5. Environment Configuration

**File**: [`app/config.py`](../backend/app/config.py)

| Setting | Default | Production Requirement |
|---------|---------|----------------------|
| `DEBUG` | `False` | Must be `False` |
| `SECRET_KEY` | `""` (rejected) | Must be ≥ 32 chars, generated securely |
| `DATABASE_URL` | required | Must be non-empty |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Recommend ≤ 60 in production |
| `TRUSTED_HOST_ENABLED` | `False` | Set `True` with `TRUSTED_HOSTS` in production |
| `RATE_LIMIT_ENABLED` | `False` | Flag present; enforcement planned |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:3000"]` | Must restrict to production origin |
| `REPORT_SCHEDULER_ENABLED` | `False` | Keep `False` in API workers |

**Hardening applied in Phase 7.21.2**:
- `SECRET_KEY` validator rejects empty or short keys.
- `DATABASE_URL` validator rejects empty values.
- `TRUSTED_HOST_ENABLED` / `TRUSTED_HOSTS` / `RATE_LIMIT_ENABLED` added.

**Remaining gap**: `ACCESS_TOKEN_EXPIRE_MINUTES=1440` in `.env` (24 hours). Reduce to 60 minutes for production.

---

## 6. Dependency Versions

**File**: [`requirements.txt`](../backend/requirements.txt)

| Package | Version Constraint | Risk |
|---------|-------------------|------|
| `fastapi` | `>=0.115.0` | Low — stable API |
| `uvicorn[standard]` | `>=0.30.0` | Low |
| `pydantic` | `>=2.8.0` | Low — v2 API |
| `pydantic-settings` | `>=2.4.0` | Low |
| `sqlalchemy` | `>=2.0.32` | Low — v2 API |
| `alembic` | `>=1.13.2` | Low |
| `psycopg2-binary` | `>=2.9.9` | Low (binary wheel) |
| `asyncpg` | `>=0.29.0` | Not used currently (async engine not configured) |
| `python-jose[cryptography]` | `>=3.3.0` | Medium — JWT library; pin to minor |
| `bcrypt` | `>=4.2.0` | Low |
| `apscheduler` | `>=3.10,<4.0` | ✅ Upper bound prevents v4 breaking changes |

**Findings**:
- `asyncpg` is listed but not used (the engine uses `psycopg2`). Consider removing to reduce surface area.
- All version constraints use `>=` with no upper bound except `apscheduler`. Consider pinning exact versions in a production lockfile.

---

## 7. Authentication Dependencies

**File**: [`app/auth/dependencies.py`](../backend/app/auth/dependencies.py)

The authentication chain:
```
oauth2_scheme (Bearer token extraction)
    → decode_jwt_token() (verify signature + expiry)
    → db.query(User) (validate user still exists in DB)
    → User object returned
```

RBAC hierarchy:
```
require_owner         → OWNER only
require_supervisor    → OWNER, SUPERVISOR
require_team_lead     → OWNER, SUPERVISOR, TEAM_LEADER
require_authenticated → any authenticated user
```

Resource-level authorization:
- `authorize_project_access` — scopes by supervisor/team assignment
- `authorize_worker_access` — scopes by supervisor/team/self
- `authorize_team_access` — scopes by supervisor/own team
- `authorize_task_access` — scopes by project/team/own tasks
- `authorize_blocker_access` — delegates to project access
- `authorize_notification_ownership` — user-owns check

**Findings**: ✅ No missing major authorization guards identified across the 12 routers. The RBAC model is correctly applied at both the role and resource level.

---

## 8. Scheduler Startup Behavior

**Files**: [`app/scheduler/scheduler.py`](../backend/app/scheduler/scheduler.py), [`app/scheduler/coordinator.py`](../backend/app/scheduler/coordinator.py)

The APScheduler is configured with:
- `max_instances=1` — prevents concurrent tick executions.
- `coalesce=True` — misfire recovery runs once instead of accumulating.
- `misfire_grace_time=30s` — allows brief startup delay.
- `timezone="UTC"` — explicit, no local-time ambiguity.

The coordinator tick:
1. Recovers stale runs (configurable timeout).
2. Queries due schedules with `WITH FOR UPDATE SKIP LOCKED` (PostgreSQL-compatible, safe with concurrent workers).
3. Executes each due schedule atomically.

**Findings**: ✅ Well-designed. The architecture documentation correctly states that the scheduler should run as a separate process in production (`python -m app.scheduler.worker`) rather than inside API workers.

---

## 9. Database Schema Review

### Indexes
All foreign key columns have `index=True`. Frequently-filtered columns (`status`, `role`, `health`, `priority`, `is_active`, `next_run_at`) also have indexes. ✅

### Unique Constraints
| Table | Column(s) | Constraint |
|-------|-----------|-----------|
| `users` | `email` | `unique=True` |
| `teams` | `name` | `unique=True` |
| `supervisors` | `user_id` | `unique=True` |
| `team_leaders` | `user_id`, `team_id` | `unique=True` |
| `workers` | `user_id` | `unique=True` |
| `report_runs` | `(schedule_id, scheduled_for)` | Composite unique index |
| `report_runs` | `execution_key` | `unique=True` |

### Cascade Behavior
- User deletion cascades to profile records (supervisor, team_leader, worker).
- Project deletion cascades to tasks, blockers, and activities.
- Schedule deletion cascades to report runs.
- Team/supervisor deletions set FKs to NULL (preserving history).

### Notable Design Choices
- `Blocker.created_date` is a `Date` (not `DateTime`) — intentional; use `Blocker.project.updated_at` for ordering.
- `ReportSchedule.scope_id` has no FK constraint — intentional polymorphism (scope can be project, team, or worker).
- N+1 patterns: RBAC filtering is done in-memory after a full list query. Acceptable at current scale; consider `joinedload` or server-side filtering if query times grow.

---

## 10. Exception Handling (Post 7.21.2)

After Phase 7.21.2 hardening, the exception hierarchy is:

| Exception | HTTP Status | Handler |
|-----------|------------|---------|
| `AuthenticationException` | 401 | `authentication_handler` |
| `EntityNotFoundException` | 404 | `not_found_handler` |
| `PermissionDeniedException` | 403 | `permission_handler` |
| `DuplicateEntityException` | 409 | `duplicate_handler` |
| `ValidationException` | 422 | `validation_handler` |
| `BusinessRuleException` | 400 | `business_rule_handler` |
| `StarletteHTTPException` | varies | `http_exception_handler` (normalizes raw HTTPException) |
| `RequestValidationError` | 422 | `request_validation_handler` (sanitizes Pydantic ctx) |
| `Exception` (catch-all) | 500 | `unhandled_exception_handler` (sanitized, logged) |

All responses use the flat envelope: `{"success": bool, "error": str, "detail": any}`.

---

## Open Items for Subsequent Phases

| Item | Phase |
|------|-------|
| Structured logging configuration | 7.21.5 |
| `/ready` readiness endpoint with DB probe | 7.21.6 |
| `RequestContextMiddleware` (X-Request-ID) | 7.21.5 |
| Deployment checklist | 7.21.7 |
| Remove unused `asyncpg` dependency | Future |
| Reduce `ACCESS_TOKEN_EXPIRE_MINUTES` to 60 in production | Pre-deployment |
| Disable OpenAPI docs in production | Pre-deployment |
| Pin exact dependency versions in a lockfile | Pre-deployment |
