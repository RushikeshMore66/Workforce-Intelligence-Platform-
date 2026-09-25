# 08 — User & Account Lifecycle

**Purpose**: This document explains the complete identity and user management system for the Workforce Intelligence Platform. It is written for developers learning the codebase.

---

## 1. Core Concepts

The platform distinguishes three types of "status" that are easy to conflate:

| Concept | Field | Model | Meaning |
|---------|-------|-------|---------|
| Account lifecycle | `User.is_active` | `User` | Can the account log in? |
| Operational status | `Worker.status` | `Worker` | Is the worker available for work? |
| Project state | `Project.status` | `Project` | What phase is the project in? |

These are **independent**. A worker can be `ACTIVE` operationally (available for tasks) but have a deactivated account (`is_active=False`). They are not interchangeable.

---

## 2. User Lifecycle

```
OWNER
  → POST /api/v1/users
    → UserManagementService.create_user()
      → validate email uniqueness
      → hash password (bcrypt)
      → create User row (is_active=True by default)
      → create role-specific profile
      → write UserAuditLog (USER_CREATED)
      → commit (atomic)
  → User can now log in via POST /api/v1/auth/login
```

### Account States

| State | `is_active` | Login Allowed | Description |
|-------|------------|---------------|-------------|
| Active | `True` | Yes | Default state for all created users |
| Deactivated | `False` | No | Owner-initiated; data preserved |

**Transition rules:**
- Only an OWNER can deactivate or reactivate a user.
- An OWNER cannot deactivate their own account.
- Deactivation does not delete data.

---

## 3. Role Profile Rules

Every user has a base `User` record plus a role-specific profile record.

### OWNER
An OWNER has only a `User` record. OWNER accounts **cannot be created via the API** — they are bootstrapped through `backend/seed.py` (development) or a dedicated initialization script (production). This is intentional: the API forbids it with a 403 error.

### SUPERVISOR
```
User (role=SUPERVISOR) + Supervisor profile
```
The `Supervisor` record has only a `user_id` foreign key. Teams and projects are assigned to supervisors after creation.

### TEAM_LEADER
```
User (role=TEAM_LEADER) + TeamLeader profile
```
`TeamLeader.team_id` is the single source of truth for which team this leader leads. At most one team. Null means "not yet assigned."

### WORKER
```
User (role=WORKER) + Worker profile
```
The `Worker` record has:
- `role` (VARCHAR) — the job title/description (not to be confused with `User.role`)
- `team_id` — FK to `teams`
- `team_leader_id` — FK to `team_leaders` (must lead the same team)
- `supervisor_id` — FK to `supervisors` (must manage the same team, if team is specified)
- `status` — operational: ACTIVE, ON_LEAVE, UNAVAILABLE
- `active_project_id` — current project assignment

---

## 4. Organizational Integrity Rules

These are enforced by `UserManagementService` at creation time:

1. **Worker + team_leader_id**: If a team leader ID is provided, that team leader must have `TeamLeader.team_id == worker.team_id`. A worker's team leader must lead the same team.

2. **Worker + team_leader without team**: If `team_leader_id` is provided, `team_id` must also be provided.

3. **Worker + supervisor + team**: If both supervisor and team are provided, the supervisor must manage that team (`Team.supervisor_id == supervisor.id`).

4. **Team leader + team**: If a team ID is provided for a team leader, that team must exist.

5. **OWNER cannot be created via API**: The `create_user` service raises `PermissionDeniedException` if `role=OWNER` is requested.

**Atomicity**: All of the above is validated within a single database transaction. If any validation fails, the entire `create_user` call rolls back — no partial state (e.g., User without profile) can exist.

---

## 5. Authentication Flow

```
POST /api/v1/auth/login
  Request: { email, password }
  → AuthService.authenticate_user()
    → look up User by email
    → if not found → return None (401)
    → if wrong password → return None (401)
    → if is_active == False → return None (401, same response shape)
    → create_jwt_token(user_id, role) → JWT
  Response: { access_token, token_type, expires_in }
  Side effect: HttpOnly cookie "access_token" is set

On every subsequent request:
  → get_current_user() dependency
    → extract token from Authorization header OR "access_token" cookie
    → decode JWT → get user_id
    → load User from database (never trust token claims alone)
    → if user.is_active == False → 401 (immediate, no token expiry wait)
    → return User
```

**Security note**: `is_active` is checked on **every request** (not just at login). This means deactivating a user takes effect immediately — even if they have a valid, unexpired JWT.

---

## 6. Current User Profile Flow

```
GET /api/v1/auth/me
  → get_current_user() dependency
  → _build_current_user_out(user) → CurrentUserOut

Response includes:
  - id, name, email, role, company, avatar_initials, is_active
  - worker_profile_id: str | null
  - supervisor_profile_id: str | null
  - team_leader_profile_id: str | null
```

The profile IDs allow the frontend to directly reference a user's profile record without scanning all workers/supervisors by email. This is the **correct** way to identify a user's profile — not email matching.

---

## 7. Profile Update Flow

### Own profile (any authenticated user)
```
PATCH /api/v1/auth/me
  Request: { name?, company?, avatar_initials? }
  → UserManagementService.update_own_profile()
    → updates only safe fields
    → writes UserAuditLog (USER_UPDATED)
  Response: CurrentUserOut (updated)
```

Role and `is_active` **cannot** be changed through this endpoint. This is enforced by the Pydantic schema `UpdateProfileRequest` which excludes those fields.

### Password change (any authenticated user)
```
POST /api/v1/auth/change-password
  Request: { current_password, new_password (min 8 chars) }
  → UserManagementService.change_password()
    → verify current_password against stored bcrypt hash
    → if wrong: raise BusinessRuleException (400)
    → hash new_password using bcrypt
    → store hashed password
    → writes UserAuditLog (PASSWORD_CHANGED)
  Response: 204 No Content
```

**JWT note**: After password change, existing JWT tokens remain valid until expiry. This is a deliberate choice for the stateless JWT architecture. For immediate session invalidation across devices, the user should log out manually. This is documented in the router code.

---

## 8. Owner User Management

All endpoints require `role=OWNER` (enforced at the router layer by `_require_owner`):

| Method | Path | Action |
|--------|------|--------|
| `GET` | `/api/v1/users` | List all users |
| `GET` | `/api/v1/users/{id}` | Get specific user |
| `POST` | `/api/v1/users` | Create user + profile |
| `PATCH` | `/api/v1/users/{id}` | Update allowed fields |
| `POST` | `/api/v1/users/{id}/activate` | Re-activate account |
| `POST` | `/api/v1/users/{id}/deactivate` | Deactivate account |

**Backend enforcement**: The `_require_owner` dependency checks `current_user.role != OWNER` and raises `PermissionDeniedException(403)` if true. Frontend role-hiding is supplementary UX only — the backend is the authoritative gate.

---

## 9. Audit Trail

All account lifecycle events are captured in the `user_audit_logs` table:

| Event | Trigger |
|-------|---------|
| `USER_CREATED` | `create_user()` |
| `USER_UPDATED` | `update_user()` or `update_own_profile()` |
| `USER_ACTIVATED` | `activate_user()` |
| `USER_DEACTIVATED` | `deactivate_user()` |
| `PASSWORD_CHANGED` | `change_password()` |

Each record captures: `target_user_id`, `actor_user_id`, `actor_name` (snapshot), `event`, `description`, `timestamp`. Actor name is stored as a snapshot to survive user deletion.

---

## 10. Authorization Matrix (Enforced by Backend)

| Operation | OWNER | SUPERVISOR | TEAM_LEADER | WORKER |
|-----------|-------|------------|-------------|--------|
| List all users | ✅ | ❌ 403 | ❌ 403 | ❌ 403 |
| Create user | ✅ | ❌ 403 | ❌ 403 | ❌ 403 |
| Deactivate/activate user | ✅ | ❌ 403 | ❌ 403 | ❌ 403 |
| Update own profile | ✅ | ✅ | ✅ | ✅ |
| Change own password | ✅ | ✅ | ✅ | ✅ |
| Change own role | ✅* | ❌ | ❌ | ❌ |
| View own profile (/auth/me) | ✅ | ✅ | ✅ | ✅ |

*Role changes require an OWNER to use `PATCH /api/v1/users/{id}`, not the self-update endpoint.

---

## 11. Key Files

### Backend

| File | Purpose |
|------|---------|
| `backend/app/models/user.py` | User, Supervisor, TeamLeader, Worker, UserRoleEnum, WorkerStatusEnum |
| `backend/app/models/user_audit.py` | UserAuditLog, UserAuditEventEnum |
| `backend/app/services/user_management_service.py` | All user lifecycle logic |
| `backend/app/services/auth_service.py` | Login / `is_active` check |
| `backend/app/auth/dependencies.py` | `get_current_user` — JWT decode + `is_active` check per request |
| `backend/app/auth/jwt.py` | JWT create / decode |
| `backend/app/routers/users.py` | Owner user management API |
| `backend/app/routers/auth.py` | Login, /me, profile update, change password |
| `backend/app/schemas/user.py` | UserCreate, UserUpdate, UserOut, role profile schemas |
| `backend/app/schemas/auth.py` | LoginRequest, TokenResponse, CurrentUserOut, etc. |
| `backend/migrations/versions/a1b2c3d4e5f6_add_is_active_and_user_audit_logs.py` | Migration: is_active + user_audit_logs |

### Frontend

| File | Purpose |
|------|---------|
| `src/lib/auth/AuthProvider.tsx` | Auth context: user state, login, logout, refreshUser |
| `src/lib/auth/useAuth.ts` | Hook to consume auth context |
| `src/lib/api/auth.ts` | login, logout, getCurrentUser, updateProfile, changePassword |
| `src/lib/api/users.ts` | getUsers, createUser, updateUser, activateUser, deactivateUser |
| `src/lib/api/client.ts` | Base HTTP client with camelCase transform + 401 handler |
| `src/lib/api/mappers.ts` | toCamelCase (responses) / toSnakeCase (requests) |
| `src/types/user.ts` | User, ManagedUser, CreateUserPayload, WorkerProfileCreate, etc. |
| `src/app/(app)/admin/page.tsx` | Owner user management page with Create User + lifecycle controls |
| `src/app/(app)/settings/page.tsx` | User profile + change password page |
| `src/components/admin/CreateUserModal.tsx` | Create User form with role-specific fields |
| `src/components/settings/EditProfileModal.tsx` | Edit own profile modal |
| `src/components/settings/ChangePasswordModal.tsx` | Change password modal |

---

## 12. Development vs Production

### Development Seed (`backend/seed.py`)
Provides demo accounts with known passwords for local development. **Never expose seed passwords in the UI or commit production credentials.** Seeded accounts use the same bcrypt hashing as production.

### Production User Provisioning
Owners create users through `POST /api/v1/users`. The system uses application-level provisioning — no seed dependency in production.

---

## 13. Common Mistakes to Avoid

1. **Do not trust role from JWT alone** — always load user from DB (`get_current_user` does this correctly).

2. **Do not confuse `Worker.status` with `User.is_active`** — they are independent. Deactivating an account uses `is_active`, not `Worker.status`.

3. **Do not bypass the service layer** — business rules (org integrity, audit events, duplicate checks) live in `UserManagementService`. Routers should not access the DB directly.

4. **Do not return `hashed_password`** — All API schemas (`UserOut`, `CurrentUserOut`) exclude it. The `User` ORM model has it; never serialize it to a response.

5. **Do not let the frontend determine role** — The `role` field in JWT is supplementary for quick UX decisions. The database truth must always be verified for authorization checks.
