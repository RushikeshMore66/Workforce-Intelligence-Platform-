# Security Hardening Report (Phase 6)

This document summarizes the security status of the Workforce Intelligence Platform backend, explicitly delineating what is implemented versus what remains as a known limitation or future work.

## IMPLEMENTED

### Password Hashing
- Replaced the deprecated `passlib` library with direct use of the modern `bcrypt` Python library.
- This resolves Python 3.11+ incompatibility issues (the 72-byte truncation bug in passlib) without weakening production hashes.
- Production and testing environments now use the identical bcrypt implementation. The temporary `sha256` test-only hash workaround was entirely removed.

### Authentication (JWT)
- **401 Unauthorized** is strictly returned for missing, invalid, or expired tokens.
- Secret keys and algorithms are correctly configured via environment variables.
- User identity is extracted from the JWT `sub` claim but validated against the active PostgreSQL database. 
- Inactive user state checks are available based on the worker's status.

### Role-Based Access Control (RBAC)
- All protected endpoints strictly enforce roles (OWNER, SUPERVISOR, TEAM_LEADER, WORKER).
- Role claims in the JWT are used but the database remains the ultimate source of truth.
- **403 Forbidden** is strictly returned when authenticated users attempt operations beyond their role.

### Resource Authorization & IDOR Protection
- Endpoints taking IDs (e.g., `/{id}`) enforce database-level relationship checks (`authorize_project_access`, `authorize_task_access`, etc.).
- A user possessing a valid `task_id` cannot access or modify the task unless the business rules permit it (e.g., they are the assignee, or their team is assigned to the parent project).
- Work updates (`POST /tasks/{task_id}/updates`) validate the submitter against the parent task's authorized access scope. Workers can only update their own assigned tasks.

### Dashboard Scope
- `GET /dashboard/activities` is now strictly scoped using database relationship checks. It only returns activities related to projects the authenticated user is authorized to access.
- `GET /dashboard/metrics` and `GET /dashboard/attention` remain organization-wide (see Known Limitations).

---

## KNOWN LIMITATIONS

### JWT and LocalStorage Limitations
- JWTs are currently stored in the frontend's `localStorage`. This is a known architectural vulnerability to XSS attacks.
- Migration to `HttpOnly` secure cookies requires structural changes to both the backend middleware and the frontend API client.

### Dashboard Scope
- The dashboard metrics (`GET /dashboard/metrics`) and attention items (`GET /dashboard/attention`) return organization-wide aggregate data to all authenticated roles.
- **Rationale:** Restricting this requires complex aggregation logic that doesn't map 1:1 with existing relationship checks, and the frontend currently expects a unified organizational dashboard. This exposes macro-level business volume data but no sensitive PII.

### Supervisor Visibility
- The supervisor endpoints (`GET /supervisors`) return a list of all supervisors to all authenticated users.
- **Rationale:** This is required by the frontend to populate project assignment dropdowns across various organizational views. It leaks names and emails of supervisors.

### User Management
- The system currently lacks any APIs for creating, modifying, or deactivating users. User provisioning happens directly in the database.
- Because the APIs do not exist, there is no privilege escalation risk from them.

---

## FUTURE WORK

### Security Event Logging
- A dedicated audit logging architecture is needed to track authentication failures, 403 Forbidden events, and future role changes. See `SECURITY_LOGGING.md`.

### Refresh Tokens
- Sessions currently expire silently upon JWT expiration. A robust refresh-token rotation architecture is required to improve UX without compromising token lifespan security.

### User Management API
- Implement OWNER-only administrative endpoints for account provisioning, deactivation, and role modification.
