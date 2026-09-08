# Teams API Integration (Phase 7.7)

## Overview
This document outlines the architecture and integration of the Teams module with the live FastAPI backend, implemented in Phase 7.7.

## Endpoints Connected
The Teams module retrieves data using the centralized `apiClient`:
- **`GET /api/v1/teams`**: Returns a list of teams authorized for the authenticated user.
- **`GET /api/v1/teams/:id`**: Returns team details (`TeamOut` schema).
- **`GET /api/v1/teams/:id/workers`**: Returns workers assigned to the team (`WorkerOut` schema).

## Data-Flow Architecture
- **`useTeams` Hook**: Orchestrates data state (`isLoading`, `error`, `data`) for the teams list.
- **`useTeamDetail` Hook**: Orchestrates data state for the team detail view, combining `getTeamById` and `getTeamWorkers`.
- **API Service (`src/lib/api/teams.ts`)**: Defines precise bindings matching FastAPI schemas exactly. Global mock fetches for team leaders, supervisors, and projects have been strictly isolated from the real-mode flow.

## Removed Global Mocks & Fabricated Fields
To enforce the Workforce boundary (Phase 7.8), the following global mock calls and unsupported metrics were entirely purged from the Teams module:
- `getAllTeamLeaders()`, `getTeamLeaderById()`
- `getSupervisorById()`
- `getWorkers()` (global)
- `getProjects()` (global)
- The global metrics for "Total Completed", "Total In Progress", and "Total Blocked" tasks were completely removed from the Team Card and Team Detail views since they were computed via dummy data and aren't natively aggregated on the backend SQLAlchemy Team model.
- Supervisor and Team Lead names display as `'—'` since only IDs are provided by the current backend schema.

## Security & Error Boundaries
- **Native RBAC Scoping**: The frontend completely relies on FastAPI's `get_teams()` authorization matrix to return only teams the user is allowed to view. No client-side filtering simulates security.
- **401 Unauthorized**: Passed through `apiClient` to trigger login redirect.
- **403 Forbidden**: Specifically handled natively inside the `ProjectDetailPage` using the professional `<AccessDenied />` boundary.
- **404 Not Found**: Displayed cleanly using a dedicated fallback UI within the Team Detail route if a team doesn't exist or is unavailable.
- **500 Server Error**: Handled dynamically presenting a "Retry" prompt.

## Mock vs Real Mode
- `NEXT_PUBLIC_USE_MOCK=false`: Forces strictly isolated FastAPI endpoints with zero mock mixing.
- `NEXT_PUBLIC_USE_MOCK=true`: Leverages local static `localStorage`-backed repository logic natively.

## Next Steps
The global Workforce module (Phase 7.8) will be integrated in subsequent iterations to unlock full global views of workers, performance, and productivity.
