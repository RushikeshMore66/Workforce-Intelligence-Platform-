# Case Study 03 — Project and Task Workflow

## Goal

Understand the operational engine.

## Project vs Task

Project:

> A larger organizational outcome.

Task:

> A concrete unit of work that contributes to that outcome.

## Project statuses

- PLANNED
- ACTIVE
- ON_HOLD
- COMPLETED
- CANCELLED

## Task statuses

- PLANNED
- IN_PROGRESS
- ON_HOLD
- COMPLETED
- CANCELLED

## Why not use "INCOMPLETE"?

Because "incomplete" is not a lifecycle state.

An ACTIVE project may simply have unfinished tasks.

## Task transition example

```
PLANNED
   ↓
IN_PROGRESS
   ↓
COMPLETED
```

or:

```
IN_PROGRESS
   ↓
ON_HOLD
   ↓
IN_PROGRESS
```

## Why transition rules exist

Without a workflow engine, users could accidentally do:

`COMPLETED -> IN_PROGRESS`

or:

`PLANNED -> COMPLETED`

The business should decide which transitions are legal.

## TaskTransition

Every status change records:

- task
- old status
- new status
- user
- time
- reason when applicable

That creates an audit trail.

## Project progress

Progress comes from tasks.

It is not simply:

`User types 73%`

Instead:

`Task state -> calculated progress`

## Project completion gate

A project cannot become completed if active tasks remain unfinished.

This creates a connection:

`Task execution -> Project truth`

## What I should be able to explain

> "Projects describe lifecycle and outcomes. Tasks describe execution. Task transitions are controlled and auditable. Project progress is derived from task completion, so management status reflects operational reality."

## Study exercise

Read together:

1. `backend/app/models/task.py`
2. `backend/app/services/task_workflow_service.py`
3. `backend/app/services/project_progress_service.py`
4. `backend/app/services/project_workflow_service.py`
5. `backend/app/routers/tasks.py`
6. `backend/app/routers/projects.py`

