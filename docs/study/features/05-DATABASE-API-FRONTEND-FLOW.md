# Case Study 05 — Database, API and Frontend Flow

## Goal

Understand how one button in the browser becomes a database change.

## The three worlds

### Frontend

User interaction.

### Backend

Business rules and security.

### Database

Persistent operational truth.

## Example: worker marks task complete

### 1. UI

Worker clicks:

**Mark Complete**

### 2. API module

Frontend calls:

`changeTaskStatus()`

File:

`src/lib/api/tasks.ts`

### 3. HTTP client

`src/lib/api/client.ts`

Adds:

- API base URL
- Authorization header
- JSON
- timeout
- error handling

### 4. Router

Backend receives:

`POST /tasks/{task_id}/status`

File:

`backend/app/routers/tasks.py`

### 5. Policy

Task scope is checked.

File:

`backend/app/authorization/policies.py`

### 6. Workflow service

Business rule is checked.

File:

`backend/app/services/task_workflow_service.py`

### 7. ORM

SQLAlchemy updates the task.

### 8. Transition

A `TaskTransition` record is created.

### 9. Progress

Project progress is recalculated.

### 10. Activity

A `ProjectActivity` record is written.

### 11. Transaction

The changes are committed together.

### 12. Response

Updated task returns to the browser.

## Why this architecture matters

It prevents business rules from living only in React components.

The same business rule works for:

- web frontend
- future mobile application
- future integration
- future automation agent

because the backend remains authoritative.

## Study exercise

Pick any API operation and draw:

`UI -> API module -> client -> router -> policy -> service -> repository/model -> DB`

Do this until it feels natural.

