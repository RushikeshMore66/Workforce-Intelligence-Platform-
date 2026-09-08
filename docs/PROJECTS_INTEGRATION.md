# Projects API Integration (Phase 7.5)

## Overview
This document outlines the architecture and integration of the Projects module with the live FastAPI backend. This integration covers the projects list, creation, update, and detail views (including scoped sub-resources).

## Endpoints Connected
The Projects module retrieves and mutates data using the following backend endpoints via the centralized `apiClient`:
- **`GET /api/v1/projects`**: Returns a list of projects, accepting native filters (`search`, `status`, `health`, `priority`).
- **`GET /api/v1/projects/:id`**: Returns project details, mapping exactly to `ProjectDetailOut` (`teamIds`, `teamCount`).
- **`POST /api/v1/projects`**: Creates a new project based on `ProjectCreate` schema.
- **`PATCH /api/v1/projects/:id`**: Updates project properties based on `ProjectUpdate` schema.
- **`GET /api/v1/projects/:id/tasks`**: Returns tasks specifically scoped to the project.
- **`GET /api/v1/projects/:id/blockers`**: Returns blockers specifically scoped to the project.
- **`GET /api/v1/projects/:id/activities`**: Returns activities specifically scoped to the project.

## Data-Flow Architecture
The integration adheres to a strict hook-driven architecture, avoiding direct UI `fetch` calls.

1. **`useProjects` Hook**: Orchestrates data state (`isLoading`, `error`, `projects`) for the project list. Dynamically propagates filter query parameters.
2. **`useProjectDetail` Hook**: Provides lazy-loading state orchestration for project subresources. Uses separate API bindings for `tasks`, `blockers`, and `activities`.
3. **API Service (`src/lib/api/projects.ts`)**: Defines precise bindings matching FastAPI schemas exactly (e.g. mapping `team_count` inherently through the `apiClient` mapping wrapper).

## Mock vs Real Mode
- `NEXT_PUBLIC_USE_MOCK=false`: Forces the application to strictly use FastAPI endpoints. It guarantees no silent mock data leaks into the real production state.
- `NEXT_PUBLIC_USE_MOCK=true`: Leverages local, static `localStorage`-backed repository logic, completely bypassing the backend. Global teams/workers calls were deliberately scoped out of this phase.

## Loading & Error States
- **Loading State**: Sections display unified skeleton components (`<SkeletonTable>`, `<SkeletonCard>`) during resolution, avoiding layout shifts.
- **Lazy Tab Loading**: Project Detail tabs fetch sub-resources lazily to conserve initial mount bandwidth. E.g., `fetchTasks()` is invoked only upon activating the "Tasks" tab.
- **401 Unauthorized**: Handled transparently by `apiClient` which terminates the session and triggers a login redirect.
- **403 Forbidden**: Specifically handled natively inside the `ProjectDetailPage` and `CreateProjectDialog`. Employs professional `<AccessDenied />` boundaries or form-level error badges instead of terminating the user session.
- **404 Not Found**: A dedicated Not Found UI is presented cleanly within `ProjectDetailPage`.
- **Validation Errors (422)**: Caught explicitly within mutations (e.g., project creation) mapping to server form messages natively.
- **Empty States**: Professionally presented zeros without relying on dummy data insertion.

## RBAC Authorization UX vs Backend Authority
The UI utilizes the authenticated user role strictly to conditionally hide actions (e.g., `Create Project` button is visible only to `OWNER` / `SUPERVISOR`).
However, actual capability is **enforced unconditionally by the backend router logic**. Attempting unauthorized transactions triggers graceful `403` catches which inform the user visually.

## Refetch Behavior
Upon completing a state mutation (such as a successful `POST /projects`), the dialog triggers a direct `refetch()` method natively provided by `useProjects`, achieving synchronization without refreshing the entire browser context or injecting additional libraries like React Query.

## Current Limitations & Exclusions
- The Global `Workers` and `Teams` modules were strictly excluded from integration at this stage. Detailed global lists or user mappings fallback natively.
- Project Detail's `Team` tab will display an informational banner deferring full integration to the Phase 7.8 (Workforce) window.
- The `Dashboard` logic intentionally avoids consuming `getProjects` until Phase 7.6.
