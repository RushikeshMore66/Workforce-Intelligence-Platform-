# Workforce Intelligence Platform — Complete Project Structure & Study Guide

> **Study purpose:** Use this file when you do not know where something belongs.
>
> Do not try to memorize every file. Learn the flow:
>
> **Browser -> API client -> FastAPI router -> authorization -> service -> repository/ORM -> PostgreSQL -> response -> browser**

---

# 1. Repository map

Current study branch:

`workflow-hardening`

The repository is a full-stack application:

```
Workforce-Intelligence-Platform-/
│
├── backend/                 # FastAPI + PostgreSQL backend
│   ├── app/
│   ├── migrations/
│   ├── tests/
│   └── requirements.txt
│
├── src/                    # Next.js frontend
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── types/
│
├── docs/                   # Existing technical documentation
│
├── public/                 # Static frontend assets
├── package.json            # Frontend dependencies/scripts
├── next.config.ts
├── eslint.config.mjs
└── setup scripts / project metadata
```

---

# 2. Backend architecture

The backend follows a layered architecture.

```
HTTP Request
     │
     ▼
Router
     │
     ├── Authentication
     ├── Authorization
     └── Request validation
     │
     ▼
Service
     │
     ├── Business rules
     ├── workflow rules
     └── calculations
     │
     ▼
Repository / SQLAlchemy ORM
     │
     ▼
PostgreSQL
```

The important lesson:

> **Router should not contain every business rule.**

The router receives the request.

The service decides what the business operation means.

The repository/model layer handles data access.

---

# 3. backend/app

## core files

### `backend/app/main.py`

Application entry point.

Understand:

- FastAPI application creation
- router registration
- middleware
- exception handling
- health endpoints

### `backend/app/config.py`

Configuration/settings.

### `backend/app/database.py`

Database infrastructure.

Understand:

- SQLAlchemy engine
- Base
- DB session
- dependency used by routers

---

# 4. backend/app/auth

```
auth/
├── dependencies.py
└── jwt.py
```

### jwt.py

Responsible for:

- creating JWT tokens
- decoding JWT tokens
- token claims

### dependencies.py

Responsible for turning:

`Bearer Token -> authenticated User`

The important concept is:

> The token identifies the user, but the database is used to resolve the current user.

---

# 5. backend/app/authorization

```
authorization/
├── dependencies.py
├── permissions.py
├── policies.py
└── roles.py
```

This is the security brain.

### roles.py

Defines role-to-permission relationships.

### permissions.py

Defines named capabilities.

Example idea:

`PROJECT_CREATE`

### dependencies.py

Provides reusable permission checks.

### policies.py

Provides object-level scope rules.

Example:

> Supervisor can access a project only when the project belongs to that supervisor's scope.

This distinction is extremely important:

### Permission

"Can this role perform this type of action?"

### Policy

"Can this specific user perform the action on this specific object?"

---

# 6. backend/app/models

ORM/database representation.

Current core models include:

```
user.py
team.py
project.py
task.py
blocker.py
notification.py
activity.py
report_run.py
report_schedule.py
```

Think:

`Model = how the data exists in the database.`

---

# 7. The most important model relationships

```
User
 ├── Supervisor
 ├── TeamLeader
 └── Worker

Supervisor
 └── Teams

Team
 ├── Workers
 ├── Team Leader
 └── Projects

Project
 ├── Supervisor
 ├── Teams
 ├── Tasks
 ├── Blockers
 └── Activities

Task
 ├── Assignee
 ├── Team
 ├── Work Updates
 ├── Task Transitions
 └── Blockers
```

This is the heart of the domain.

---

# 8. backend/app/schemas

Pydantic request/response contracts.

Examples:

- project create/update/status change
- task create/update/status change
- worker responses
- authentication requests/responses
- analytics responses

Think:

`Schema = what the API accepts or returns.`

Do not confuse:

`Model != Schema`

Model = database representation.

Schema = API contract.

---

# 9. backend/app/repositories

Repositories isolate database access.

Important examples:

`project_repo.py`

`task_repo.py`

`team_repo.py`

`worker_repo.py`

The repository layer helps keep SQL/data-access code separate from business rules.

---

# 10. backend/app/services

This is one of the most important folders to study.

Examples:

```
auth_service.py
project_service.py
project_workflow_service.py
project_progress_service.py
task_workflow_service.py
team_service.py
worker_service.py
dashboard_service.py
analytics_service.py
report_service.py
report_execution_service.py
```

### The key mental model

#### project_service.py

Normal project operations.

#### project_workflow_service.py

Rules such as:

`PLANNED -> ACTIVE`

`ACTIVE -> ON_HOLD`

`ACTIVE -> COMPLETED`

#### project_progress_service.py

Derives project progress from task states.

#### task_workflow_service.py

Rules such as:

`PLANNED -> IN_PROGRESS`

`IN_PROGRESS -> COMPLETED`

`IN_PROGRESS -> ON_HOLD`

These workflow services are examples of putting business rules in one place instead of scattering them throughout UI code.

---

# 11. backend/app/routers

Routers are the HTTP interface.

Current major routers include:

```
auth.py
projects.py
tasks.py
teams.py
workers.py
supervisors.py
dashboard.py
analytics.py
reports.py
notifications.py
blockers.py
health.py
metrics.py
```

Mental model:

`Router = API door`

Examples:

`POST /projects`

`POST /tasks/{id}/status`

`GET /workers/{id}/tasks`

---

# 12. Why task status has a dedicated endpoint

A generic patch such as:

`PATCH /tasks/{id}`

can accidentally become a free-for-all.

The project therefore separates:

### Metadata edit

`PATCH /tasks/{id}`

from:

### Workflow transition

`POST /tasks/{id}/status`

This lets the workflow engine validate:

- allowed transition
- current state
- user scope
- worker restrictions
- required hold reason
- audit record

This is a very important production design lesson.

---

# 13. Database migrations

`backend/migrations/`

Alembic maintains database schema history.

Important idea:

`Python model change != automatic production database change`

The migration records how the database structure changes safely.

The task workflow migration is a concrete example of:

- old task statuses
- new task statuses
- enum migration
- transition reason field

---

# 14. Tests

`backend/tests/`

Tests verify:

- authentication
- authorization
- project behavior
- task workflow
- dashboard
- workers
- security
- scheduler
- reports
- observability
- health
- metrics

When studying the project, tests are often easier to understand than implementation first.

Recommended technique:

> Read a test -> identify expected behavior -> read the service -> read the router.

---

# 15. Frontend architecture

The frontend is Next.js.

```
src/app
src/components
src/lib
src/types
```

---

# 16. src/app

App Router pages.

```
src/app/
├── login/
└── (app)/
    ├── dashboard/
    ├── projects/
    ├── teams/
    ├── workforce/
    ├── supervisors/
    ├── my-work/
    ├── notifications/
    ├── settings/
    ├── analytics/
    ├── reports/
    └── intelligence/
```

Think:

> `app/` decides what URL/page exists.

---

# 17. src/app/(app)

This is the authenticated application area.

The layout wraps the pages with:

- authentication protection
- role protection
- sidebar
- topbar

Important file:

`src/app/(app)/layout.tsx`

---

# 18. src/components

Reusable visual pieces.

### auth

Authentication/authorization UI.

### dashboard

Dashboard-specific visual components.

### layout

Sidebar/topbar/application shell.

### projects

Project-specific badges and UI.

### reports

Report components.

### settings

Settings UI.

### ui

Generic reusable components such as:

- buttons
- badges
- inputs
- tables
- tabs
- dialogs
- progress
- skeletons

---

# 19. src/lib/api

This is the frontend's API boundary.

Important file:

`src/lib/api/client.ts`

It handles:

- API base URL
- bearer token
- fetch
- errors
- timeout
- snake_case/camelCase transformation

Domain API modules then call it:

```
projects.ts
tasks.ts
teams.ts
workers.ts
auth.ts
dashboard.ts
analytics.ts
reports.ts
notifications.ts
```

Mental model:

`Page -> API module -> apiClient -> FastAPI`

---

# 20. src/lib/auth

```
AuthProvider.tsx
rbac.ts
storage.ts
types.ts
useAuth.ts
```

### storage.ts

Browser token storage.

### AuthProvider

Keeps current authenticated user in React state.

### useAuth

Convenient access to authentication state.

### rbac.ts

Frontend visibility rules.

Important:

> Frontend RBAC is for user experience. Backend authorization remains the real security boundary.

---

# 21. src/types

Frontend domain contracts.

Examples:

```
user.ts
team.ts
project.ts
task.ts
blocker.ts
activity.ts
notification.ts
analytics.ts
report.ts
dashboard.ts
```

Think:

`Type = what the frontend believes the API data looks like.`

---

# 22. Complete request example: worker completes a task

Study this until you can draw it yourself.

### Step 1

Worker clicks:

**Mark Complete**

### Step 2

Frontend calls:

`changeTaskStatus(taskId, { status: "COMPLETED" })`

### Step 3

API module sends:

`POST /tasks/{taskId}/status`

### Step 4

FastAPI router receives request.

### Step 5

Authorization policy checks:

- Is the task real?
- Can this worker access it?
- Is this their task?

### Step 6

TaskWorkflowService validates:

- current status
- allowed transition

### Step 7

Database update occurs.

### Step 8

TaskTransition is created.

### Step 9

Project progress is recalculated.

### Step 10

Project activity is recorded.

### Step 11

Database transaction commits.

### Step 12

Updated task returns to frontend.

### Step 13

Worker UI updates.

That is the architecture you should be able to explain confidently.

---

# 23. Complete request example: project completion

```
Owner/Supervisor
       ↓
POST /projects/{id}/status
       ↓
authorize_project_access()
       ↓
recalculate project progress
       ↓
ProjectWorkflowService
       ↓
check task states
       ↓
if unfinished active task exists
       ↓
reject
```

The important business idea:

> Project status cannot lie about the work underneath it.

---

# 24. "Which file do I edit?"

| Requirement | Main place |
|---|---|
| New database field | model + Alembic migration + schema if exposed |
| New API endpoint | router |
| Business rule | service |
| Scope/security | authorization policies/permissions |
| Database query abstraction | repository |
| Frontend API call | src/lib/api |
| Frontend page | src/app |
| Reusable visual | src/components |
| Shared frontend data shape | src/types |
| Authentication state | src/lib/auth |
| Project workflow | project_workflow_service.py |
| Task workflow | task_workflow_service.py |
| Progress calculation | project_progress_service.py |

This table is one of the most important things to remember.

---

# 25. Why the architecture is reusable

The system separates:

### Stable operational engine

- identity
- roles
- teams
- projects/jobs
- tasks/work
- workflow
- events
- analytics

from:

### Industry-specific meaning

For software:

`Task = API implementation`

For automation:

`Task = PLC commissioning`

For manufacturing:

`Task = machining operation`

For field service:

`Task = customer-site repair`

The software architecture remains similar while the business vocabulary changes.

---

# 26. Study order

Do not study the project randomly.

### Stage 1 — Understand the product

Read:

`docs/study/PROJECT_PRD.md`

### Stage 2 — Understand the map

Read this file.

### Stage 3 — Learn identity

Study:

- User
- Worker
- TeamLeader
- Supervisor
- JWT
- RBAC

### Stage 4 — Learn work

Study:

- Project
- Task
- TaskStatus
- TaskTransition
- WorkUpdate

### Stage 5 — Learn business rules

Study:

- project workflow
- task workflow
- project progress

### Stage 6 — Learn request flow

Trace one request from:

Frontend -> API -> Router -> Authorization -> Service -> Database

### Stage 7 — Learn intelligence

Study:

- dashboard
- analytics
- reports
- intelligence

---

# 27. Questions you should be able to answer

Before saying you fully understand the project, answer these without opening the code:

1. Why do we have both User and Worker?
2. Why are permissions and policies separate?
3. Why can't a worker patch project status?
4. Why is task status a dedicated endpoint?
5. Why do we store TaskTransition?
6. Why is project progress derived?
7. Why do we have services and repositories?
8. Why does frontend call an API module instead of fetch everywhere?
9. Where does authentication happen?
10. Where is authorization actually enforced?
11. What happens when a worker marks a task completed?
12. How would you adapt the system to a manufacturing company?
13. How would you adapt it to an automation agency?
14. Which parts should remain reusable?
15. Which parts should become industry-specific?

If you can answer those, you understand the architecture rather than merely recognizing filenames.

---

# 28. Local-study note

The repository contains many existing technical audit documents. These new study documents are intentionally different.

Existing docs answer:

> "How did we implement/fix this?"

The study docs answer:

> "What problem are we solving, why does this architecture exist, and how can I explain it to another person?"
