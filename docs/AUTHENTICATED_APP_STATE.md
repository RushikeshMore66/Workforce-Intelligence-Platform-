# Authenticated Application State

This document describes the Phase 7.3 implementation of the authenticated application state and frontend Role-Based Access Control (RBAC).

## 1. Single Canonical Authenticated User
The frontend relies entirely on a single canonical representation of the user, derived from the `GET /api/v1/auth/me` endpoint. 
- The state is owned by `AuthProvider`.
- We do not duplicate context or state for users.
- `useAuth()` hook provides `{ user, isAuthenticated, isLoading }`.

## 2. Authentication vs Authorization
- **401 (Unauthenticated)**: The user's token is invalid, expired, or missing. The global API client listener (`setUnauthorizedCallback`) clears the auth state and forces a redirect to the `/login` page.
- **403 (Forbidden)**: The user is authenticated but doesn't have permissions to view a resource or perform an action. This is handled by rendering a 403 `AccessDenied` view, preventing a redirect to `/login`.

## 3. Route Protection
We implemented a hierarchical protection model:
1. `ProtectedRoute`: Validates if a user is authenticated. Wraps the main layout to ensure no unauthenticated user can view the app.
2. `RoleGuard`: Validates if the authenticated user has access to the current section. Used in the `(app)/layout.tsx` to protect both static and dynamic routes recursively.

## 4. Frontend RBAC (UX Only)
The frontend RBAC is purely for UX to hide buttons and navigate flows. **The backend remains the authoritative security boundary.**

### Page Permissions
- `/dashboard`: OWNER, SUPERVISOR, TEAM_LEADER, WORKER
- `/projects`: OWNER, SUPERVISOR, TEAM_LEADER, WORKER
- `/supervisors`: OWNER
- `/teams`: OWNER, SUPERVISOR, TEAM_LEADER
- `/workforce`: OWNER, SUPERVISOR, TEAM_LEADER, WORKER
- `/analytics`: OWNER
- `/reports`: OWNER
- `/intelligence`: OWNER
- `/notifications`: All roles
- `/settings`: All roles

> **Note on Teams UX:** The `Teams` navigation is restricted to `OWNER`, `SUPERVISOR`, and `TEAM_LEADER` for UX purposes. Workers can still access their team info through their own dashboard or workforce context. This is a frontend UX decision.

> **Note on Reports & Intelligence:** These sections currently have no backend API contracts, and are strictly restricted to `OWNER` for Phase 7.3.

## 5. Mock vs Real Mode
The application can run in mock mode by setting `NEXT_PUBLIC_USE_MOCK=true`. In this mode, login generates a dummy token and `GET /auth/me` resolves to a hardcoded `OWNER` user. Real mode uses the backend endpoints `/api/v1/auth/login` and `/api/v1/auth/me`.

## 6. Login Return URL
The `/login` route parses the `next` query parameter. It strictly validates the path to prevent open redirects by ensuring it starts with `/` but not `//`.
