# Phase 7.21.3 — Database Reliability Review

**Audit Date**: 2026-09-12  
**Platform**: Workforce Intelligence Platform  
**Scope**: PostgreSQL configuration, SQLAlchemy session lifecycle, Alembic migrations, constraints, indexes, and transaction boundaries.

---

## 1. Database Configuration

- **Connection Health Checks**: SQLAlchemy engine is configured with `pool_pre_ping=True`, meaning connections are validated before use. This handles stale connections transparently.
- **Session Lifecycle**: Handled via FastAPI dependency injection (`get_db()` with `Yield`). Sessions are properly closed in a `finally` block, and errors trigger `db.rollback()` before being raised. This prevents broken sessions from being reused across requests.
- **Startup Discipline**: The application strictly relies on Alembic for schema changes. No internal `Base.metadata.create_all()` code is executed during standard API worker startup, making it safe for multiple concurrent workers.
- **Credentials**: `DATABASE_URL` is sourced safely from environment variables and checked for emptiness at startup.

---

## 2. Schema Integrity & Indexes

### Indexes
All critical querying columns are indexed.
- **Foreign Keys**: `project_id`, `task_id`, `user_id`, `team_id`, etc.
- **Filters**: `status`, `role`, `priority`, `health`, `is_active`, `next_run_at`.

### Constraints & Types
- **Blocker Dates**: `created_date` correctly uses `Date` (without time), reflecting business logic that blockers are tracked by day.
- **Unique Constraints**:
  - `users.email`
  - `teams.name`
  - `supervisors.user_id`, `team_leaders.user_id`, `workers.user_id`
  - `team_leaders(user_id, team_id)`
  - `report_runs.execution_key`
- **Polymorphism**: `ReportSchedule.scope_id` intentionally lacks a foreign key constraint because it can map to a Project, Team, or Worker depending on `report_type`.

### Cascade Behavior
- Hard deletes on `User` cascade to profiles (`Supervisor`, `TeamLeader`, `Worker`).
- Hard deletes on `Project` cascade to `Task`, `Blocker`, and `ProjectActivity`.
- Hard deletes on `ReportSchedule` cascade to `ReportRun`.
- Most soft deletes (e.g. removing a worker from a team) use `ondelete="SET NULL"` to preserve historical integrity for analytics.

---

## 3. Migration Integrity

**Alembic Chain Status:**
- History is linear and sequential.
- There is exactly one head: `e06e69fd8b2e`.
- The database is fully up to date and can be reconstructed from scratch without errors.

No new migrations were required for Phase 7.21.3 as all necessary constraints, cascades, and indexes are already present in the schema.

---

## 4. Transaction Boundaries & Concurrency

### Atomic Transactions
- **Task Update**: `TaskService.update_task` applies the state change, creates a `TaskTransition` (if status changed), creates a `ProjectActivity` log, and then calls `db.commit()` once. This is atomic.
- **Work Update**: `add_work_update` creates the update and commits atomically.

### Non-Atomic Transactions (Acceptable & Documented)
- **Project Creation**: `ProjectService.create_project` delegates project creation to `repo.create()`, which issues a commit. It then adds a `ProjectActivity` and commits again.
  - *Risk*: A crash between the two commits leaves a Project without an initial creation activity log.
  - *Mitigation/Acceptance*: This is an acceptable failure mode as the core entity (Project) is persisted. The activity log is a secondary auditing feature. 
- **Report Scheduling Execution**: The scheduler claims a run and commits the claim. It generates the report to disk. It then marks the run as complete and commits again.
  - *Risk*: If generation fails, the run remains in a RUNNING or pending state.
  - *Mitigation/Acceptance*: This is intentional. Large reports can take time to generate. The scheduler uses a state machine and staleness checks to handle interrupted runs. Committing the claim first is necessary to prevent duplicate concurrent executions.

---

## 5. Reliability Verification Tests

Extensive reliability tests have been added to `tests/test_database_reliability.py` to ensure:
1. `IntegrityError` is properly caught when creating duplicate users.
2. The database session remains usable after catching and rolling back an `IntegrityError`.
3. Foreign key constraints correctly reject invalid data insertions (e.g., non-existent user).
4. `execution_key` uniqueness is enforced to prevent double-generation of the same report slot.
5. Unique constraints correctly enforce that a Team cannot have two Team Leaders pointing to the same User/Team combination.
