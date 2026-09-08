# Dashboard API Integration (Phase 7.4)

## Overview
This document outlines the architecture and integration of the Dashboard UI with the live FastAPI backend. The Dashboard aggregates organizational metrics, attention items, and recent project activities.

## Dashboard Endpoints Connected
The dashboard retrieves data from three unified backend endpoints using the centralized API client:
- **`GET /api/v1/dashboard/metrics`**: Returns aggregate KPI statistics (active projects, total workers, etc.).
- **`GET /api/v1/dashboard/attention`**: Returns items requiring immediate review (blockers, deadlines).
- **`GET /api/v1/dashboard/activities`**: Returns a list of recent `ProjectActivity` records.

## Data-Flow Architecture
The architecture implements a single-direction data flow strictly isolated from direct UI fetches:
1. **`useDashboard` Hook**: Orchestrates data state (`isLoading`, `data`, `error`) and provides retry mechanisms.
2. **Dashboard API Service (`src/lib/api/dashboard.ts` & `activities.ts`)**: Defines specific API bindings and conditionally loads mock behavior depending on the `.env.local` settings.
3. **`apiClient`**: Securely attaches the JWT via localStorage, handles 401 interceptors, converts backend `snake_case` properties to `camelCase`.
4. **FastAPI Backend**: Serves validated data from PostgreSQL.

## Mock vs Real Mode
- `NEXT_PUBLIC_USE_MOCK=false`: Forces the application to strictly use FastAPI endpoints. It guarantees no silent mock data leaks into the real production state.
- `NEXT_PUBLIC_USE_MOCK=true`: Leverages local, static, or `localStorage`-backed repository logic, completely bypassing the backend.

## Error and Loading Behaviors
- **Loading State**: Sections display unified skeleton components (`<SkeletonCard>`) while data resolves, avoiding jarring layout shifts.
- **Partial Failure**: Sections (Metrics, Attention, Activities) fail independently. If `metrics` succeeds but `attention` fails, the rest of the dashboard remains completely usable.
- **Retry Logic**: Each failed section presents a dedicated "Retry" button. Invoking retry calls the API Service without reloading the browser window.
- **Empty State**: Supported implicitly by evaluating the array length or null states directly via React JSX conditionals. It is explicitly designed to handle `0` workers, `0` projects, etc.
- **401 Unauthorized**: Handled transparently by `apiClient` which logs the user out.
- **403 Forbidden**: Avoids un-authenticating the user. Error boundaries gracefully contain the layout.

## Role & Scope Behavior
The Dashboard APIs inherently enforce RBAC restrictions on the backend. The frontend simply maps and displays what the server provides:
- **OWNER**: Views organization-wide activities and unrestricted attention items.
- **SUPERVISOR / TEAM_LEADER / WORKER**: Activity feeds and attention endpoints are internally scoped by the backend to their respective projects and assigned teams.

## Known Backend Limitations
- **Project Details**: The dashboard metrics API currently only supplies aggregate project counts. A UI table `ProjectHealthTable` requires detailed project/supervisor arrays. Because direct implementation of the Phase 7.5 `/projects` API was restricted, `ProjectHealthTable` correctly renders an empty state placeholder pending future integration.
