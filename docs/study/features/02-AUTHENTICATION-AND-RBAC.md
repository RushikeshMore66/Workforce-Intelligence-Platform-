# Case Study 02 — Authentication and RBAC

## Goal

Understand how the system knows who the user is and what they are allowed to do.

## Authentication

Authentication answers:

> Who are you?

The platform uses:

`email/password -> JWT -> current User`

Important files:

- `backend/app/auth/jwt.py`
- `backend/app/auth/dependencies.py`
- `backend/app/services/auth_service.py`
- `src/lib/auth/AuthProvider.tsx`
- `src/lib/auth/storage.ts`

## Authorization

Authorization answers:

> What are you allowed to do?

Roles:

- OWNER
- SUPERVISOR
- TEAM_LEADER
- WORKER

## Two levels of authorization

### Permission

Example:

> Supervisor can update tasks.

### Policy

Example:

> Supervisor can update only tasks belonging to projects inside their scope.

This is stronger than simple role checks.

## Important security principle

Frontend hiding a button is not security.

Real security happens in the backend.

The frontend RBAC exists mainly for:

- navigation
- usability
- preventing confusing actions

The backend decides whether the request is legal.

## Example

Worker attempts:

`POST /tasks/task-123/status -> COMPLETED`

Backend checks:

1. authenticated user
2. worker profile
3. task ownership
4. current status
5. valid transition

Only then is the change accepted.

## What I should be able to explain

> "Authentication establishes identity with JWT. Authorization then applies role permissions and object-level policies. That means a worker can operate on assigned tasks without gaining access to unrelated organization data."

## Study exercise

Trace this:

`Login page -> auth API -> JWT -> AuthProvider -> getCurrentUser -> Sidebar visibility`

Then trace:

`Worker request -> get_current_user -> authorize_task_access`

