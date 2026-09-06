# Authorization Audit — Phase 5

## Findings Summary

This document records every security gap discovered during the Phase 5 authorization audit of the backend.

---

## 1. `get_current_user()` Implementation

**Status: EXISTS — but has a critical security bypass.**

`backend/app/auth/dependencies.py` defines `get_current_user()` correctly for the token path, but includes a dangerous development fallback:

```python
if not token:
    # Fallback for development/demo mode if Authorization header is missing:
    owner_user = db.query(User).filter(User.role == UserRoleEnum.OWNER).first()
    if owner_user:
        return owner_user
    raise credentials_exception
```

**This is a critical security vulnerability.** Any unauthenticated request to any protected endpoint falls through as the OWNER user if the database contains an owner. This must be removed before production.

**Fix:** Remove the `if not token:` fallback. Always require a valid token.

---

## 2. Role Dependencies

**Status: PARTIALLY IMPLEMENTED — gaps exist.**

`RoleChecker`, `require_owner`, `require_supervisor`, `require_team_lead` exist and are used on some routes. However:

- `POST /projects` and `PATCH /projects/{id}` use `require_supervisor` — correct in principle.
- All other write endpoints (tasks, blockers, etc.) use only `get_current_user`, accepting **any role**.
- No worker-scope enforcement exists anywhere.

---

## 3. Endpoint-by-Endpoint Findings

### GET /api/v1/auth/login
**Auth required:** No ✅ Correct.

### GET /api/v1/auth/me
**Auth required:** Yes ✅  
**Resource scope:** Returns authenticated user's own profile ✅

### GET /api/v1/dashboard/metrics, /attention, /activities
**Auth required:** Yes ✅  
**Role restriction:** None — any authenticated user sees organization-wide dashboard data ⚠️  
**Resource scope:** None — returns all metrics/activities regardless of user role ❌

### GET /api/v1/projects
**Auth required:** Yes ✅  
**Role restriction:** None — any authenticated user sees ALL projects ❌  
**Resource scope:** None — supervisors see all projects, workers see all projects ❌

### GET /api/v1/projects/{id}
**Auth required:** Yes ✅  
**Resource scope:** None — any authenticated user can fetch any project by ID ❌ (IDOR)

### POST /api/v1/projects
**Auth required:** Yes ✅  
**Role restriction:** OWNER or SUPERVISOR only ✅  
**Resource scope:** No supervisor self-assignment check ⚠️

### PATCH /api/v1/projects/{id}
**Auth required:** Yes ✅  
**Role restriction:** OWNER or SUPERVISOR only ✅  
**Resource scope:** Any supervisor can update any project (not restricted to assigned projects) ❌

### GET /api/v1/projects/{id}/tasks, /blockers, /activities
**Auth required:** Yes ✅  
**Resource scope:** None — any authenticated user can fetch tasks/blockers/activities for any project ❌

### GET /api/v1/workers
**Auth required:** Yes ✅  
**Resource scope:** None — all workers returned to all authenticated users ❌  
A worker can list every other worker in the system.

### GET /api/v1/workers/{id}
**Auth required:** Yes ✅  
**Resource scope:** None — any authenticated user can fetch any worker (IDOR) ❌

### GET /api/v1/teams
**Auth required:** Yes ✅  
**Resource scope:** None — all teams returned to all users ❌

### GET /api/v1/teams/{id}
**Auth required:** Yes ✅  
**Resource scope:** None — any authenticated user can fetch any team (IDOR) ❌

### GET /api/v1/teams/{id}/workers
**Auth required:** Yes ✅  
**Resource scope:** None — any authenticated user can list workers of any team ❌

### GET /api/v1/supervisors, GET /api/v1/supervisors/{id}
**Auth required:** Yes ✅  
**Resource scope:** None — all supervisors returned to all roles ⚠️  
(Ambiguous: workers may not need to see supervisor org data — documented below)

### GET /api/v1/tasks/{id}
**Auth required:** Yes ✅  
**Resource scope:** None — any authenticated user can fetch any task (IDOR) ❌

### POST /api/v1/tasks
**Auth required:** Yes ✅  
**Role restriction:** None — workers can create tasks ❌  
Should require OWNER or SUPERVISOR or TEAM_LEADER.

### PATCH /api/v1/tasks/{id}
**Auth required:** Yes ✅  
**Role restriction:** None — any authenticated user can update any task ❌  
A worker can update another worker's task.

### POST /api/v1/tasks/{id}/updates
**Auth required:** Yes ✅  
**Resource scope:** Sets `worker_id = current_user.id` ✅ (uses DB user, not request body)  
**But:** Any role can add a work update to any task — no task ownership check ⚠️

### GET /api/v1/blockers
**Auth required:** Yes ✅  
**Resource scope:** Returns ALL blockers in system to any authenticated user ❌

### POST /api/v1/blockers
**Auth required:** Yes ✅  
**Resource scope:** Sets `reported_by_id = current_user.id` ✅  
**But:** Any role can report a blocker on any project ⚠️

### PATCH /api/v1/blockers/{id}
**Auth required:** Yes ✅  
**Resource scope:** Any authenticated user can update/resolve any blocker ❌

### GET /api/v1/notifications
**Auth required:** Yes ✅  
**Resource scope:** Filters by `current_user.id` ✅ CORRECT — users only see their own notifications.

### PATCH /api/v1/notifications/{id}/read
**Auth required:** Yes ✅  
**Resource scope:** Fetches notification by ID — does NOT verify it belongs to current user ❌  
Any authenticated user can mark any other user's notification as read (IDOR).

### POST /api/v1/notifications/read-all
**Auth required:** Yes ✅  
**Resource scope:** Filters by `current_user.id` ✅ CORRECT.

### GET /api/v1/analytics
**Auth required:** Yes ✅  
**Role restriction:** None — any role sees organization-wide analytics ❌  
Workers should not see company-wide workforce analytics.

---

## 4. Critical Issues Ranked

| Severity | Issue |
|----------|-------|
| 🔴 CRITICAL | `get_current_user()` dev bypass grants OWNER access with no token |
| 🔴 HIGH | `GET /projects`, `GET /projects/{id}` — no supervisor/team scoping |
| 🔴 HIGH | `PATCH /tasks/{id}` — any role can update any task |
| 🔴 HIGH | `GET /blockers` — returns all blockers organization-wide |
| 🔴 HIGH | `PATCH /blockers/{id}` — any role can update any blocker |
| 🔴 HIGH | `POST /tasks` — workers can create tasks |
| 🟠 MEDIUM | `PATCH /notifications/{id}/read` — IDOR, no ownership check |
| 🟠 MEDIUM | `GET /workers`, `GET /workers/{id}` — no scope restriction |
| 🟠 MEDIUM | `GET /teams`, `GET /teams/{id}` — no scope restriction |
| 🟠 MEDIUM | `GET /analytics` — workers see org-wide analytics |
| 🟡 LOW | Dashboard endpoints return org-wide data to all roles |
| 🟡 LOW | Supervisors page visible to all authenticated users |

---

## 5. What Is Already Correct

- JWT validation via `decode_jwt_token()` ✅
- User loaded from DB (not from token claims) ✅
- `RoleChecker` dependency pattern established ✅
- Notifications scoped by `current_user.id` ✅
- `mark_all_read` scoped by `current_user.id` ✅
- Activity `reported_by_id` and `worker_id` set from authenticated user ✅
- Consistent 403 via `PermissionDeniedException` ✅
- Consistent 401 via `credentials_exception` ✅

---

## 6. Schema Assessment

No schema changes are required for Phase 5 authorization. All necessary relationships already exist:

- `Project.supervisor_id` → links to `Supervisor`
- `Team.supervisor_id` → links to `Supervisor`
- `Worker.team_id`, `Worker.supervisor_id`, `Worker.team_leader_id` → full hierarchy
- `Supervisor.projects`, `Supervisor.teams`, `Supervisor.workers` → reverse relations
- `TeamLeader.team_id`, `TeamLeader.workers` → team scope
- `Notification.user_id` → ownership

---

## 7. Business Rule Ambiguities

The following rules are **intentionally designed as permissive** for Phase 5 — documented here to make the decision explicit:

1. **Supervisors listing (`GET /supervisors`):** Accessible to all authenticated users. Rationale: All roles need to see supervisor names for project assignment UIs. No sensitive data exposed.
2. **Dashboard (`GET /dashboard/metrics`, etc.):** Accessible to all authenticated users. Rationale: The business intent is a shared org-wide dashboard. Restricting by role would require business specification outside Phase 5 scope.
3. **Workers listing (`GET /workers`):** Scoped by role — OWNER/SUPERVISOR see all; TEAM_LEADER sees own team; WORKER sees own team members only.
4. **Analytics (`GET /analytics`):** Restricted to OWNER and SUPERVISOR only.
