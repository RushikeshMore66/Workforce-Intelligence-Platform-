# API Contract — Workforce Intelligence Platform

> **Version:** 1.0  
> **Backend:** FastAPI + PostgreSQL  
> **Frontend:** Next.js 16  
> **Base URL:** `NEXT_PUBLIC_API_URL/api/v1`  
> **Authentication:** JWT Bearer Token

All authenticated endpoints require the header:
```
Authorization: Bearer <access_token>
```

---

## Error Response Format

All errors return a consistent JSON envelope:

```json
{
  "success": false,
  "error": "Not Found",
  "detail": "Project with id proj-999 not found"
}
```

Common HTTP status codes:
- `400` — Bad request / validation error
- `401` — Unauthorized (missing or expired token)
- `403` — Forbidden (insufficient role)
- `404` — Resource not found
- `409` — Duplicate entity conflict
- `422` — Unprocessable entity

---

## Auth

### POST /auth/login
Login and receive an access token.

**Auth required:** No

**Request:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response `200`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

---

### GET /auth/me
Get the currently authenticated user.

**Auth required:** Yes — any role

**Response `200`:**
```json
{
  "id": "uuid-string",
  "email": "rajesh@company.com",
  "name": "Rajesh Mehta",
  "role": "OWNER",
  "avatar_initials": "RM",
  "company": "Apex Software Solutions"
}
```

---

## Dashboard

### GET /dashboard/metrics
Aggregate metrics for the dashboard KPI cards.

**Auth required:** Yes — OWNER, SUPERVISOR

**Response `200`:**
```json
{
  "active_projects": 12,
  "completed_projects": 3,
  "total_workers": 70,
  "workers_active": 64,
  "workers_on_leave": 4,
  "workers_unavailable": 2,
  "tasks_completed": 284,
  "tasks_in_progress": 45,
  "tasks_pending": 62,
  "tasks_blocked": 8,
  "projects_on_track": 6,
  "projects_at_risk": 3,
  "projects_delayed": 2
}
```

---

### GET /dashboard/attention-items
Items requiring immediate management attention.

**Auth required:** Yes — OWNER, SUPERVISOR

**Response `200`:**
```json
[
  {
    "id": "ai-1",
    "title": "CRM Development critically behind schedule",
    "description": "28% complete with 30 days remaining",
    "priority": "HIGH",
    "project_id": "proj-3",
    "type": "RISK"
  }
]
```

---

## Projects

### GET /projects
List all projects. Supports filtering.

**Auth required:** Yes — any role (SUPERVISOR sees only assigned projects)

**Query params:**
- `status` — filter by ProjectStatus
- `health` — filter by ProjectHealth
- `priority` — filter by ProjectPriority
- `supervisor_id` — filter by supervisor

**Response `200`:** Array of Project objects

**Project object:**
```json
{
  "id": "uuid",
  "name": "Hotel Billing System",
  "client": "Grand Hotels & Resorts",
  "description": "...",
  "start_date": "2026-01-10",
  "deadline": "2026-10-31",
  "priority": "HIGH",
  "supervisor_id": "uuid",
  "status": "ACTIVE",
  "health": "ON_TRACK",
  "progress": 76,
  "created_at": "2026-01-05T09:00:00Z",
  "updated_at": "2026-08-30T10:00:00Z"
}
```

---

### POST /projects
Create a new project.

**Auth required:** Yes — OWNER only

**Request:**
```json
{
  "name": "New Project",
  "client": "Client Name",
  "description": "Project description",
  "start_date": "2026-09-01",
  "deadline": "2026-12-31",
  "priority": "HIGH",
  "supervisor_id": "uuid"
}
```

**Response `201`:** Created Project object

---

### GET /projects/{id}
Get a single project by ID.

**Auth required:** Yes

**Response `200`:** Project object with embedded teams and supervisor

---

### PATCH /projects/{id}
Partially update a project.

**Auth required:** Yes — OWNER or assigned SUPERVISOR

**Request:** Any subset of CreateProjectInput fields plus `status`, `health`, `progress`

**Response `200`:** Updated Project object

---

### DELETE /projects/{id}
Delete a project.

**Auth required:** Yes — OWNER only

**Response `204`:** No content

---

### GET /projects/{id}/tasks
List tasks for a specific project.

**Auth required:** Yes

**Response `200`:** Array of Task objects

---

### GET /projects/{id}/blockers
List blockers for a specific project.

**Auth required:** Yes

**Response `200`:** Array of Blocker objects

---

### GET /projects/{id}/activities
List activity events for a specific project.

**Auth required:** Yes

**Response `200`:** Array of ProjectActivity objects

---

## Workers

### GET /workers
List all workers.

**Auth required:** Yes

**Query params:**
- `team_id` — filter by team
- `supervisor_id` — filter by supervisor
- `project_id` — filter by active project
- `status` — filter by WorkerStatus

**Response `200`:** Array of Worker objects

**Worker object:**
```json
{
  "id": "uuid",
  "name": "Rohan Verma",
  "email": "rohan.verma@company.com",
  "role": "Senior Backend Developer",
  "team_id": "uuid",
  "team_leader_id": "uuid",
  "supervisor_id": "uuid",
  "avatar_initials": "RV",
  "status": "ACTIVE",
  "active_project_id": "uuid",
  "completed_task_count": 24,
  "in_progress_task_count": 3,
  "pending_task_count": 2,
  "blocked_task_count": 0
}
```

---

### GET /workers/{id}
Get a single worker by ID.

**Auth required:** Yes

**Response `200`:** Worker object

---

## Supervisors

### GET /supervisors
List all supervisors.

**Auth required:** Yes — OWNER

**Response `200`:** Array of Supervisor objects

**Supervisor object:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "Amit Sharma",
  "email": "amit@company.com",
  "avatar_initials": "AS",
  "project_ids": ["uuid", "uuid"],
  "team_ids": ["uuid"]
}
```

---

### GET /supervisors/{id}
Get a single supervisor by ID.

**Auth required:** Yes

**Response `200`:** Supervisor object

---

## Teams

### GET /teams
List all teams.

**Auth required:** Yes

**Query params:**
- `supervisor_id` — filter by supervisor

**Response `200`:** Array of Team objects

**Team object:**
```json
{
  "id": "uuid",
  "name": "Backend Engineering",
  "supervisor_id": "uuid",
  "leader": {
    "id": "uuid",
    "user_id": "uuid",
    "name": "Kiran Joshi",
    "email": "kiran@company.com",
    "avatar_initials": "KJ",
    "team_id": "uuid"
  },
  "worker_count": 18,
  "project_ids": ["uuid"]
}
```

---

### GET /teams/{id}
Get a single team by ID.

**Auth required:** Yes

**Response `200`:** Team object with embedded leader and workers

---

## Tasks

### GET /tasks
List tasks. Supports filtering.

**Auth required:** Yes

**Query params:**
- `project_id` — filter by project
- `team_id` — filter by team
- `assignee_id` — filter by worker
- `status` — filter by TaskStatus

**Response `200`:** Array of Task objects

**Task object:**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "title": "Implement invoice generation API",
  "description": "...",
  "assignee_id": "uuid",
  "team_id": "uuid",
  "status": "IN_PROGRESS",
  "priority": "HIGH",
  "due_date": "2026-09-30",
  "created_at": "2026-07-01T09:00:00Z",
  "updated_at": "2026-08-15T10:00:00Z"
}
```

---

### POST /tasks
Create a task.

**Auth required:** Yes — OWNER, SUPERVISOR, TEAM_LEADER

**Request:**
```json
{
  "project_id": "uuid",
  "title": "Task title",
  "description": "Description",
  "assignee_id": "uuid",
  "team_id": "uuid",
  "priority": "HIGH",
  "due_date": "2026-12-31"
}
```

**Response `201`:** Created Task object

---

### PATCH /tasks/{id}
Update a task (including status changes).

**Auth required:** Yes — OWNER, SUPERVISOR, TEAM_LEADER, or assigned WORKER

**Request:** Any subset of task fields

**Response `200`:** Updated Task object

---

## Blockers

### GET /blockers
List blockers.

**Auth required:** Yes

**Query params:**
- `project_id`
- `team_id`
- `status` — `OPEN` or `RESOLVED`

**Response `200`:** Array of Blocker objects

**Blocker object:**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "task_id": "uuid",
  "title": "PayU API credentials not received",
  "description": "...",
  "reported_by_id": "uuid",
  "team_id": "uuid",
  "created_date": "2026-08-28",
  "resolved_date": null,
  "status": "OPEN"
}
```

---

### POST /blockers
Report a new blocker.

**Auth required:** Yes — any role

**Request:**
```json
{
  "project_id": "uuid",
  "task_id": "uuid",
  "title": "Blocker title",
  "description": "Detailed description",
  "team_id": "uuid"
}
```

**Response `201`:** Created Blocker object

---

### PATCH /blockers/{id}/resolve
Mark a blocker as resolved.

**Auth required:** Yes — OWNER, SUPERVISOR, TEAM_LEADER

**Response `200`:** Updated Blocker object with `status: "RESOLVED"` and `resolved_date`

---

## Activities

### GET /activities
List recent activities across all projects.

**Auth required:** Yes

**Query params:**
- `limit` — max results (default: 20)
- `project_id` — filter by project
- `user_id` — filter by user

**Response `200`:** Array of ProjectActivity objects

**ProjectActivity object:**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "description": "Rohan Verma completed Invoice Generation API task",
  "user_id": "uuid",
  "user_name": "Rohan Verma",
  "timestamp": "2026-08-30T13:48:00Z",
  "type": "TASK_COMPLETED"
}
```

**ActivityType values:**
`PROJECT_CREATED` | `PROJECT_UPDATED` | `PROJECT_STATUS_CHANGED` | `PROJECT_ASSIGNED` |
`TASK_CREATED` | `TASK_UPDATED` | `TASK_ASSIGNED` | `TASK_STATUS_CHANGED` | `TASK_COMPLETED` |
`WORK_UPDATE_ADDED` |
`BLOCKER_REPORTED` | `BLOCKER_RESOLVED` |
`TEAM_CREATED` | `TEAM_UPDATED` | `MEMBER_ADDED` | `MEMBER_REMOVED` |
`USER_CREATED` | `USER_UPDATED`

---

## Work Updates

### GET /work-updates
List work updates.

**Auth required:** Yes

**Query params:**
- `task_id` — filter by task
- `worker_id` — filter by worker

**Response `200`:** Array of WorkUpdate objects

**WorkUpdate object:**
```json
{
  "id": "uuid",
  "task_id": "uuid",
  "worker_id": "uuid",
  "description": "Completed 70% of database migration. Testing phase starts tomorrow.",
  "timestamp": "2026-08-30T14:30:00Z"
}
```

---

### POST /work-updates
Submit a work update.

**Auth required:** Yes — WORKER, TEAM_LEADER

**Request:**
```json
{
  "task_id": "uuid",
  "description": "Update description"
}
```

**Response `201`:** Created WorkUpdate object

---

## Notifications

### GET /notifications
List notifications for the current user.

**Auth required:** Yes — any role (returns own notifications)

**Response `200`:** Array of Notification objects

**Notification object:**
```json
{
  "id": "uuid",
  "type": "BLOCKER",
  "title": "New blocker reported",
  "description": "PayU API credentials not received",
  "project_id": "uuid",
  "user_id": "uuid",
  "read": false,
  "timestamp": "2026-08-30T13:00:00Z",
  "priority": "HIGH"
}
```

**NotificationType values:** `PROJECT_ALERT` | `BLOCKER` | `DEADLINE` | `TASK` | `WORK_UPDATE` | `TEAM_UPDATE` | `SYSTEM`

**NotificationPriority values:** `LOW` | `MEDIUM` | `HIGH` | `URGENT`

---

### GET /notifications/unread-count
Get count of unread notifications.

**Auth required:** Yes

**Response `200`:**
```json
{ "count": 6 }
```

---

### PATCH /notifications/{id}/read
Mark a notification as read.

**Auth required:** Yes

**Response `200`:** Updated Notification object

---

### PATCH /notifications/read-all
Mark all notifications as read for current user.

**Auth required:** Yes

**Response `204`:** No content

---

## Analytics

### GET /analytics
Aggregate analytics data for charts.

**Auth required:** Yes — OWNER, SUPERVISOR

**Response `200`:**
```json
{
  "task_completion": [
    { "month": "Mar", "completed": 28, "in_progress": 18, "blocked": 2 }
  ],
  "team_workload": [
    { "team": "Backend", "tasks": 36, "completed": 18, "blocked": 3 }
  ],
  "project_progress": [
    { "name": "Hotel Billing", "progress": 76, "target": 80 }
  ],
  "workload_trend": [
    { "week": "Jul W1", "backend": 28, "frontend": 22, "qa": 18, "devops": 10, "uiux": 9 }
  ]
}
```

---

## Intelligence

### GET /intelligence
Management intelligence insights.

**Auth required:** Yes — OWNER, SUPERVISOR

**Response `200`:** Array of IntelligenceInsight objects

```json
[
  {
    "id": "uuid",
    "priority": "HIGH",
    "type": "RISK",
    "title": "CRM Development is critically behind schedule",
    "body": "Detailed insight body...",
    "project_id": "uuid",
    "team_id": null,
    "worker_id": null,
    "action_label": "Review CRM Project",
    "action_href": "/projects/proj-3"
  }
]
```

---

## Reports

### GET /reports
List previously generated reports.

**Auth required:** Yes — OWNER

**Response `200`:** Array of Report objects

---

### POST /reports/generate
Generate a new report.

**Auth required:** Yes — OWNER

**Request:**
```json
{
  "type": "WEEKLY_WORKFORCE",
  "start_date": "2026-08-24",
  "end_date": "2026-08-30",
  "project_id": null,
  "team_id": null
}
```

**ReportType values:** `WEEKLY_WORKFORCE` | `PROJECT_PROGRESS` | `TEAM_PERFORMANCE` | `BLOCKED_WORK` | `SUPERVISOR_SUMMARY` | `COMPANY_OVERVIEW`

**Response `201`:** Generated Report object

---

## Role Authorization Summary

| Endpoint | OWNER | SUPERVISOR | TEAM_LEADER | WORKER |
|---|---|---|---|---|
| GET /dashboard/metrics | Yes | Yes (scoped) | No | No |
| POST /projects | Yes | No | No | No |
| PATCH /projects/:id | Yes | Assigned only | No | No |
| DELETE /projects/:id | Yes | No | No | No |
| GET /workers | Yes | Scoped | Scoped | Self |
| POST /tasks | Yes | Yes | Yes | No |
| PATCH /tasks/:id | Yes | Yes | Yes | Assigned |
| POST /blockers | Yes | Yes | Yes | Yes |
| PATCH /blockers/:id/resolve | Yes | Yes | Yes | No |
| GET /analytics | Yes | Yes | No | No |
| GET /intelligence | Yes | Yes | No | No |
| POST /reports/generate | Yes | No | No | No |
