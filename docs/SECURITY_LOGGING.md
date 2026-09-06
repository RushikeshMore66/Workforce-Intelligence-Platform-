# Security Logging Architecture

## Current State
The Workforce Intelligence Platform backend currently implements general entity-level activity logging (e.g., project created, task updated) via the `ProjectActivity` model. However, it does **not** currently possess a dedicated, tamper-evident security audit logging subsystem for authentication and authorization events.

## Recommended Future Architecture

To achieve compliance and support forensic analysis, a discrete security event logging architecture is required.

### 1. Separation of Concerns
Security events must be logged independently from product activity feeds.
- **Product Activity (`activities` table)**: "User marked task complete" (Displayed in UI to users).
- **Security Audit Log (`audit_logs` table)**: "Failed login attempt for admin@example.com from IP 192.168.1.50" (Secured, immutable, admin-only).

### 2. Required Events to Log
The system should record the following events:
- **Authentication:** Login successes, login failures, token revocations.
- **Authorization:** 403 Forbidden incidents (Privilege escalation attempts, IDOR attempts).
- **User Management:** Account creation, deactivation, password changes, and role changes (when implemented).

### 3. Data to Capture
A proper security log entry should include:
- `timestamp`: UTC datetime.
- `event_type`: Standardized enum (e.g., `AUTH_FAILED`, `ACCESS_DENIED`).
- `user_id`: If authenticated, or the attempted identifier.
- `ip_address`: Extracted from the ASGI request scope.
- `resource`: URL path or resource ID targeted.
- `user_agent`: Request headers.
- `severity`: INFO, WARNING, CRITICAL.

### 4. Critical Constraints
- **Never log secrets:** Passwords, JWTs, API keys, or PII (other than email as identifier) must never be written to logs.
- **Immutability:** The audit log table should ideally be append-only at the database level.
- **Performance:** Logging should happen asynchronously or via background tasks in FastAPI (`BackgroundTasks`) to avoid blocking the main request thread.

### Implementation Next Steps (Phase 7+)
1. Create an `AuditLog` SQLAlchemy model.
2. Implement an `AuditLogger` dependency/service.
3. Inject the logger into `get_current_user` to catch auth failures.
4. Inject the logger into the `RoleChecker` and `authorize_*` helpers to catch authorization failures.
