# Role-Based Access Control (RBAC) — Phase 5

## Overview

Phase 5 implements production RBAC for the Workforce Intelligence Platform backend. This document covers the complete security model, implementation approach, and known limitations.

---

## 1. Authentication vs Authorization

| Concern | What it does | Where it lives |
|---------|-------------|----------------|
| **Authentication** | Who are you? Validates JWT, loads DB user. | `get_current_user()` in `app/auth/dependencies.py` |
| **Authorization** | What can you do? Checks role + resource scope. | `RoleChecker`, `authorize_*` helpers in `app/auth/dependencies.py` |

The frontend `ProtectedRoute` component does **not** replace backend authorization. It is purely a UX convenience to avoid showing protected UI to unauthenticated users.

---

## 2. Role Hierarchy

```
OWNER
  └── SUPERVISOR
        └── TEAM_LEADER
              └── WORKER
```

Roles are **not** automatically hierarchical in code. Each `RoleChecker` explicitly lists which roles are allowed. OWNER is explicitly included in every elevated permission group.

| Role | Description |
|------|-------------|
| `OWNER` | Unrestricted access to all organization data |
| `SUPERVISOR` | Access scoped to assigned projects and teams |
| `TEAM_LEADER` | Access scoped to own team, its workers, and their projects |
| `WORKER` | Access scoped to self, own tasks, and own team's projects |

---

## 3. Authentication Flow

```
HTTP Request with Authorization: Bearer <jwt>
      ↓
oauth2_scheme extracts token
      ↓
get_current_user()
      ↓
decode_jwt_token() — verifies signature + expiry
      ↓
Extract 'sub' (user ID) from payload
      ↓
Load User from database (DB is the source of truth)
      ↓
Return authenticated User
```

If the token is missing, expired, or tampered with → HTTP **401 Unauthorized**.

---

## 4. Role Authorization

Role checks use the `RoleChecker` dependency class. It wraps `get_current_user()` and raises HTTP **403 Forbidden** if the user's role is not in the allowed list.

```python
# Available role dependencies
require_owner       = RoleChecker([OWNER])
require_supervisor  = RoleChecker([OWNER, SUPERVISOR])
require_team_lead   = RoleChecker([OWNER, SUPERVISOR, TEAM_LEADER])
require_authenticated = get_current_user  # any valid token
```

---

## 5. Resource Authorization

Beyond role checks, most resources require **relationship-based access control**. This is enforced via these helper functions in `app/auth/dependencies.py`:

| Helper | Purpose |
|--------|---------|
| `authorize_project_access(project_id, user, db)` | Verifies user can access the project |
| `authorize_worker_access(worker_id, user, db)` | Verifies user can access the worker profile |
| `authorize_task_access(task_id, user, db)` | Verifies user can access/modify the task |
| `authorize_blocker_access(blocker_id, user, db)` | Verifies user can access/modify the blocker |
| `authorize_notification_ownership(notif_id, user, db)` | Verifies notification belongs to current user |

All helpers raise `PermissionDeniedException` (HTTP 403) when access is denied, or `EntityNotFoundException` (HTTP 404) when the resource doesn't exist.

---

## 6. IDOR (Insecure Direct Object Reference) Prevention

Before Phase 5, fetching `/workers/{id}`, `/tasks/{id}`, `/blockers/{id}`, `/projects/{id}` returned any resource to any authenticated user. This is a classic IDOR vulnerability.

Phase 5 fixes this by verifying **database relationships**, not just whether the ID resolves. Examples:

- Worker A cannot access `GET /workers/worker-B-id` unless they share a team (TEAM_LEADER) or supervisor (SUPERVISOR) relationship.
- A worker cannot `PATCH /tasks/{id}` unless the task's `assignee_id` matches their own worker profile.
- A user cannot `PATCH /notifications/{id}/read` unless `notification.user_id == current_user.id`.
- A supervisor cannot `PATCH /projects/{id}` unless `project.supervisor_id == their supervisor profile.id`.

---

## 7. HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| `401 Unauthorized` | Not authenticated | Missing token, invalid signature, expired token |
| `403 Forbidden` | Authenticated but unauthorized | Role mismatch, resource not in user's scope |
| `404 Not Found` | Resource does not exist | Resource not in DB (consistent: no 404 vs 403 oracle attack risk per object type) |

---

## 8. Frontend vs Backend Security

| Layer | Mechanism | Security Boundary? |
|-------|-----------|-------------------|
| Frontend `ProtectedRoute` | Checks `isAuthenticated` from `useAuth()` | ❌ No — UX only |
| Frontend role checks | Reads `user.role` for UI visibility | ❌ No — UX only |
| Backend `get_current_user()` | JWT validation + DB load | ✅ Yes |
| Backend `RoleChecker` | Role enforcement | ✅ Yes |
| Backend `authorize_*` helpers | Resource-level scoping | ✅ Yes |

Never trust frontend role information. Always verify on the backend for every request.

---

## 9. RBAC NOT Implemented

The following authorization concerns are **out of scope for Phase 5** and should be addressed in future phases:

- User management: who can create/update/delete user accounts?
- Supervisor assignment: who can assign a supervisor to a project?
- Team management: who can add/remove workers from teams?
- Fine-grained task assignment (only team leader for their team, etc.)
- Cross-organization multi-tenancy
- Audit logging for authorization events

---

## 10. Future HttpOnly Cookie Migration

Token storage currently uses `localStorage` (frontend). If the backend adds HttpOnly cookie support:
1. Update `backend/app/main.py` to include session cookie middleware.
2. Add cookie-based login and logout endpoints.
3. Update `src/lib/auth/storage.ts` (frontend) — this single module isolates the change.
4. No changes needed in UI components.
