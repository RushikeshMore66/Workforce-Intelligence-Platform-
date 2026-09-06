# Domain Model Architecture

The Workforce Intelligence Platform frontend is strictly aligned with the FastAPI backend model architecture. This document outlines the data flow from the backend API down to the UI components.

## Architecture Stack

Data flows through five distinct layers:

1. **Backend / API (Source of Truth)**
   - The FastAPI backend defines canonical schemas (e.g., `WorkerOut`, `TeamOut`, `ActivityTypeEnum`).
   - Fields are defined in `snake_case`.
   - Examples: `completed_task_count`, `avatar_initials`.

2. **Frontend DTOs & Mappers**
   - The API Client (`src/lib/api/client.ts`) handles generic `snake_case` to `camelCase` conversion globally.
   - Because the generic conversion exists, explicit Mappers and separate API DTOs are **only** created where the API representation materially differs from the frontend domain representation.
   - **Rule**: React components must **never** perform `snake_case` -> `camelCase` conversion. They only deal with `camelCase` domain objects.

3. **Canonical Domain Models**
   - Defined in `src/types/`.
   - Exact mirrors of the Backend schemas but in `camelCase`.
   - Examples: `Worker`, `Team`, `Project`, `ActivityType`.
   - If the backend schema explicitly defines a derived metric (e.g., `member_count` on `TeamOut`), it is included in the canonical domain type (`memberCount` on `Team`).

4. **ViewModels / Metrics Types**
   - ViewModels extend the canonical Domain Models with frontend-only computed fields, presentation data, or client-side aggregations.
   - Examples: `WorkerViewModel`, `TeamViewModel`, `ProjectViewModel`.
   - Components use ViewModels to avoid tightly coupling UI logic (like grouping, derived color coding) to the pure canonical data.

5. **UI Components**
   - React components consume either Canonical Domain Models or ViewModels.
   - UI components are strictly typed and never rely on arbitrary assumptions about data existence.

## Core Models

### User / Auth
- `User`: Canonical representation of an authenticated user. The `CurrentUser` concept has been removed; `User` is used universally.
- Authentication responses produce `AuthTokens` (e.g., `accessToken`).

### Workspace Hierarchy
- **Project**: Represents a client initiative. Uses `ProjectViewModel` for metrics like computed team counts.
- **Team**: Represents a group of workers. Uses `TeamViewModel` for client-side aggregations.
- **Worker**: The base employee representation. Uses `WorkerViewModel`.
- **TeamLeader / Supervisor**: Role-specific projections of a User, managing Teams and Projects.

### Work Execution
- **Task**: Represents work items assigned to workers.
- **Blocker**: Issues blocking tasks.
- **WorkUpdate**: Daily or periodic status updates.
- **Activity**: Activity streams tracking platform events. `ActivityType` enum strictly matches backend schema.
- **Notification**: Alerts delivered to users. `NotificationType` enum strictly matches backend schema.

## Rules & Best Practices

1. **Backend as Source of Truth**: Never invent fields on a canonical model. If the backend doesn't support it, don't add it.
2. **ViewModel Separation**: Do not pollute canonical domain types with purely client-side metrics or UI state. Use ViewModels for that purpose.
3. **Mappers**: Add manual mappers (`.mapper.ts`) only when structural changes are needed beyond simple camelCase transformation.
4. **Enums**: Enum values (e.g., `ActivityType`, `ProjectStatus`) must identically match the backend to ensure type safety over the wire.
