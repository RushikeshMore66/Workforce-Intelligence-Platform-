# Dashboard Project Health Integration (Phase 7.6)

## Overview
This document outlines the architecture and integration of the Dashboard's Project Health section with the live FastAPI backend, implemented in Phase 7.6.

## Endpoints Connected
The Dashboard consumes data using the centralized `apiClient` through the `useDashboard` hook, specifically:
- **`GET /api/v1/projects`**: Returns the list of projects available to the authenticated user.

## Data-Flow Architecture
- **`useDashboard` Hook**: We extended the `useDashboard` hook to orchestrate the data state (`isLoading`, `error`, `data`) for projects, alongside metrics, attention items, and activities. This avoids duplicating fetching logic and keeps the Dashboard state centralized.
- **`ProjectHealthTable` Component**: Receives `projects` directly from `useDashboard`. It manages its own empty state gracefully if no active projects are returned. The global supervisors fetch was intentionally avoided to strictly respect Phase 7.6 boundaries, relying on graceful `'—'` fallbacks.

## Loading & Error States
- **Loading State**: Displays unified skeleton components (`<SkeletonCard>`) during resolution, avoiding layout shifts, identical to the other Dashboard sections.
- **Error State**: Rendered completely independently from other Dashboard components. If `getProjects()` fails, the Project Health section will display a professional error message with a dedicated "Retry" button. Other sections (Metrics, Attention, Activities) continue to function.
- **Empty States**: If no active projects exist for the authenticated user, the UI renders a professional empty state inside the table ("No active projects found") rather than attempting to render phantom projects.

## Security & RBAC Enforcement
- Frontend role checks were intentionally bypassed in favor of native backend authority.
- The Dashboard `getProjects` call inherently receives only the scoped data that the authenticated user is authorized to see (e.g., `OWNER`/`SUPERVISOR` sees all, `WORKER` sees assigned). No client-side filtering of `teamIds` or `workers` is necessary to restrict visibility.

## Exclusions (Strict Phase Boundaries)
- No global Supervisor, Teams, or Workers APIs were called.
- CRUD behaviors, authentication flows, and RBAC architecture remain untouched.
- No third-party fetching libraries like React Query or SWR were introduced.
