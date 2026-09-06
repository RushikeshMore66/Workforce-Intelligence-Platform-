# API Architecture

This document describes the Phase 3 API Service Architecture for the Workforce Intelligence Platform frontend.

## 1. Overview

The frontend architecture introduces a clean API service layer that seamlessly switches between a local mock repository and the real FastAPI backend, governed by the `NEXT_PUBLIC_USE_MOCK` environment variable.

Components should strictly consume the **Service Layer** and should not contain fetch logic, mock repository imports, or environment toggles.

```
React Component
      ↓
Feature/API Service (e.g. src/lib/api/projects.ts)
      ↓ (Decision point based on NEXT_PUBLIC_USE_MOCK)
  [ Mock Repo ]   OR   [ apiClient ]
                             ↓
                        [ FastAPI ]
```

## 2. API Client (`src/lib/api/client.ts`)

The central API client handles all HTTP requests to the backend. It provides:
- Base URL resolution from `NEXT_PUBLIC_API_URL`
- Default 10-second request timeout (via `AbortController`)
- Query parameter serialization via the `params` object
- Auth header abstraction (via `getAuthHeaders()`)
- Automatic conversion of snake_case API responses to camelCase
- Consistent error formatting via `ApiRequestError`

## 3. Error Handling

All failed API requests are normalized into the `ApiRequestError` class.
To help UI components handle errors uniformly, use the helpers from `src/types/api.ts`:

- `ApiErrorCode`: Categorizes errors (`NETWORK_ERROR`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `VALIDATION_ERROR`, `SERVER_ERROR`, `UNKNOWN`)
- `classifyApiError(status: number)`: Helper function to determine the `ApiErrorCode`.
- `isApiError(err)`: Type guard exported from `src/lib/api/client.ts`.

## 4. Environment Variables

- `NEXT_PUBLIC_API_URL`: The base URL of the FastAPI backend (e.g., `http://localhost:8000`).
- `NEXT_PUBLIC_USE_MOCK`: Set to `"true"` to use mock repositories instead of real HTTP requests.

## 5. Endpoints & Services Status

| Service | Endpoint | Method | Backend Status |
|---------|----------|--------|----------------|
| **Auth** | `/api/v1/auth/login` | POST | IMPLEMENTED |
| | `/api/v1/auth/me` | GET | IMPLEMENTED |
| **Dashboard** | `/api/v1/dashboard/metrics` | GET | IMPLEMENTED |
| | `/api/v1/dashboard/attention` | GET | IMPLEMENTED |
| | `/api/v1/dashboard/activities` | GET | IMPLEMENTED |
| **Projects** | `/api/v1/projects` | GET, POST | IMPLEMENTED |
| | `/api/v1/projects/:id` | GET, PATCH | IMPLEMENTED |
| | `/api/v1/projects/:id/tasks` | GET | IMPLEMENTED |
| | `/api/v1/projects/:id/blockers` | GET | IMPLEMENTED |
| | `/api/v1/projects/:id/activities` | GET | IMPLEMENTED |
| **Workers** | `/api/v1/workers` | GET | IMPLEMENTED |
| | `/api/v1/workers/:id` | GET | IMPLEMENTED |
| **Teams** | `/api/v1/teams` | GET | IMPLEMENTED |
| | `/api/v1/teams/:id` | GET | IMPLEMENTED |
| | `/api/v1/teams/:id/workers` | GET | IMPLEMENTED |
| | `/api/v1/team-leaders/*` | GET | NOT AVAILABLE |
| **Tasks** | `/api/v1/tasks/:id` | GET, PATCH | IMPLEMENTED |
| | `/api/v1/tasks` | POST | IMPLEMENTED |
| | `/api/v1/tasks` (List All) | GET | NOT AVAILABLE |
| | `/api/v1/tasks/:id/updates` | POST | IMPLEMENTED |
| | `/api/v1/tasks/:id/updates` | GET | NOT AVAILABLE |
| **Blockers** | `/api/v1/blockers` | GET, POST | IMPLEMENTED |
| | `/api/v1/blockers/:id` | PATCH | IMPLEMENTED |
| **Supervisors** | `/api/v1/supervisors` | GET | IMPLEMENTED |
| | `/api/v1/supervisors/:id` | GET | IMPLEMENTED |
| **Analytics** | `/api/v1/analytics` | GET | IMPLEMENTED |
| **Notifications** | `/api/v1/notifications` | GET | IMPLEMENTED |
| | `/api/v1/notifications/:id/read` | PATCH | IMPLEMENTED |
| | `/api/v1/notifications/read-all` | POST | IMPLEMENTED |
| **Users** | `/api/v1/users/*` | Any | NOT AVAILABLE |
| **Reports** | `/api/v1/reports/*` | Any | NOT AVAILABLE |
| **Intelligence**| `/api/v1/intelligence/*`| Any | NOT AVAILABLE |
| **Activities** | `/api/v1/activities` (Global)| GET | NOT AVAILABLE |

> **Note**: For `NOT AVAILABLE` endpoints, the frontend services will throw an Error when `NEXT_PUBLIC_USE_MOCK=false`. Mock implementations remain for UI development purposes.

## 6. Authentication Abstraction

Phase 3 introduces an abstraction point for authentication `getAuthHeaders()`.
Currently, this is a mock implementation that relies on `localStorage`. **This is temporary**. Phase 4 will introduce proper secure JWT token management, refresh token rotation, and robust authentication contexts. Components should rely on `useAuth()` (which will be fully powered in Phase 4) and avoid manipulating tokens directly.
