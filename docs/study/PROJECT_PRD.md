# Workforce Intelligence Platform — Project PRD

> **Study purpose:** This document explains what the system is supposed to solve, who uses it, why the main entities exist, and what the product is intentionally trying to become.
>
> This is not a marketing document. It is the business-and-product reference you should study before studying individual code files.

## 1. Product identity

**Project:** Workforce Intelligence Platform (WIP)

**Main motto:**
> **Solve real industrial problems through the people doing the work.**

**Product idea:**
> Turn everyday work into reliable operational intelligence.

The platform is not intended to be just an employee directory, attendance tool, or dashboard.

Its core job is to create a reliable chain:

`People + Work + Events -> Operational Truth -> Visibility -> Accountability -> Better Decisions`

The system should capture what people are actually doing, preserve who changed what, and convert that information into useful operational views.

---

## 2. The problem we are solving

In many small and medium organizations, work information can be fragmented across:

- WhatsApp messages
- Excel sheets
- meetings
- phone calls
- emails
- personal notes
- disconnected software
- manual daily/weekly reports

The operational problem is not simply "lack of dashboards."

The deeper problem is:

> Management often cannot see the current state of real work without asking multiple people.

That creates five recurring problems:

### 2.1 Work visibility

A manager needs to know:

- What work exists?
- Who owns it?
- What has started?
- What is completed?
- What is stuck?
- What is overdue?

### 2.2 Accountability

The organization should be able to answer:

- Who changed the status?
- When did it change?
- What was the old state?
- Why was work put on hold?

### 2.3 Bottleneck visibility

A task on hold is not just a status badge.

It can represent:

- waiting for client approval
- waiting for material
- waiting for another team
- missing technical information
- equipment problem
- dependency problem

The system therefore preserves reasons and transition history.

### 2.4 Manual reporting reduction

Instead of repeatedly asking:

> "Give me today's project status."

The system should already contain the operational events needed to produce that answer.

### 2.5 Decision delay

The longer operational truth stays hidden in conversations and spreadsheets, the longer management takes to react.

---

## 3. Who uses the product?

The current system has four roles.

| Role | Main responsibility |
|---|---|
| OWNER | Organization-level control and visibility |
| SUPERVISOR | Project/work coordination and management |
| TEAM_LEADER | Team-level coordination |
| WORKER | Execute assigned work and report progress |

The important design principle is:

> **People should update the part of the operation they actually control.**

A worker should not be able to arbitrarily change project lifecycle state.

A supervisor should not automatically gain owner-level access.

The backend enforces this separation.

---

## 4. Core domain

The most important business objects are:

`User -> Role -> Supervisor/TeamLeader/Worker -> Team -> Project -> Task -> WorkUpdate / TaskTransition`

Additional intelligence objects include:

- blockers
- project activities
- notifications
- analytics
- reports
- intelligence/attention views

### Project

Represents a major piece of organizational work.

### Team

Represents the people executing work together.

### Task

Represents executable work inside a project.

### Work update

Represents a human-written operational update.

### Task transition

Represents a state change with audit information.

### Project activity

Represents a timeline event that management can understand later.

---

## 5. Important workflow rule

Do not confuse **project lifecycle** with **task execution**.

### Project lifecycle

`PLANNED -> ACTIVE -> ON_HOLD -> ACTIVE -> COMPLETED`

or appropriate cancellation paths.

### Task lifecycle

`PLANNED -> IN_PROGRESS -> ON_HOLD -> IN_PROGRESS -> COMPLETED`

or cancellation paths allowed by role.

### What "incomplete" means

"Incomplete" is not a project status.

A project can be:

- PLANNED
- ACTIVE
- ON_HOLD
- COMPLETED
- CANCELLED

An active project can still be incomplete because some tasks are unfinished.

This separation is important because it keeps business language clean:

> **Project lifecycle tells us what state the project is in.**
>
> **Tasks tell us how much executable work is actually complete.**

---

## 6. Progress model

Project progress is derived from task execution.

Current concept:

`progress = completed_non_cancelled_tasks / total_non_cancelled_tasks * 100`

Cancelled tasks are excluded.

This makes progress a derived operational signal instead of an arbitrary number typed into a form.

Example:

- 10 active tasks
- 6 completed
- 2 in progress
- 2 planned

Project progress = 60%.

If 2 tasks are cancelled and 6 of the remaining 8 are completed:

Project progress = 75%.

---

## 7. Project completion rule

A project cannot be marked completed merely because a manager clicks "Complete."

The workflow checks the underlying tasks.

A project can become COMPLETED only when the active/non-cancelled work is actually completed.

This is an example of a major product principle:

> **The system should validate operational reality, not just accept management input.**

---

## 8. Worker intention

The worker is not expected to manage the entire organization.

The worker's job is simple:

1. Open their assigned work.
2. Start a task.
3. Work on it.
4. Add useful updates.
5. Put it on hold if blocked.
6. Explain why it is on hold.
7. Mark it complete when the work is actually finished.

This creates a clean operational feedback loop:

`Worker action -> Database event -> Project progress -> Supervisor visibility`

---

## 9. Supervisor intention

The supervisor's job is to control work within their scope.

The supervisor should eventually be able to answer:

- Which projects are active?
- Which teams are active?
- Which tasks are on hold?
- Which workers have too much or too little active work?
- Which deadlines are at risk?
- Which blockers need intervention?

The supervisor is therefore an operational control layer.

---

## 10. Team leader intention

The team leader coordinates execution inside the team.

The team leader should eventually be able to:

- view team members
- view team work
- understand task status
- identify blockers
- coordinate assignment
- help move work forward

---

## 11. Owner intention

The owner needs the widest organizational picture:

- overall project health
- workforce state
- project progress
- delivery trends
- reports
- analytics
- cross-team problems
- operational risks

The owner is not supposed to manually inspect every worker.

The system should summarize operational truth upward.

---

## 12. Current major feature areas

### Authentication
- Login
- JWT
- Current-user lookup
- Browser token handling

### Authorization
- Role permissions
- Scope policies
- Project/team/worker/task authorization
- Frontend route visibility
- Backend enforcement

### Projects
- Create
- View
- Update metadata
- Project lifecycle
- Project progress

### Tasks
- Create
- Update metadata
- Status transitions
- Transition history
- Work updates

### Workforce
- Worker directory
- Worker scope
- Worker metrics

### Teams
- Team management
- Team membership
- Team-level scope

### Dashboard
- Organizational metrics
- project health
- workforce overview
- work progress
- recent activity
- attention signals

### Analytics
- project analytics
- team analytics
- worker analytics
- organization analytics

### Reports
- report definitions
- report execution
- report storage
- scheduled reports
- exports

### Intelligence
- attention/risk style operational views
- future AI analysis should consume real system data

### Notifications
- actionable operational notifications

---

## 13. What this product is NOT

At the current stage, do not describe it as:

- full ERP
- complete factory MES
- accounting software
- HR payroll system
- attendance-only software
- CRM
- generic project-management clone

The platform is a **workforce execution + operational intelligence foundation**.

Industry-specific systems can be built on top of that foundation.

---

## 14. Industrial customization strategy

The same core engine can be customized for different organizations.

### Software agency

Project = client implementation

Task = development/design/testing task

Worker = developer/designer/tester

Blocker = client approval, bug dependency, missing requirement

### Automation agency

Project = automation deployment

Task = PLC configuration, panel work, integration, testing, commissioning

Worker = automation engineer/technician

Blocker = material, client access, machine availability, site issue

### Materials/manufacturing organization

Project = production/order/job

Task = machining, inspection, packing, dispatch, maintenance activity

Worker = operator/technician/inspector

Blocker = material shortage, machine downtime, quality issue

### Construction/field service

Project = site/job

Task = installation, inspection, repair, procurement, handover

Worker = field worker/engineer

Blocker = access, material, permit, equipment, client dependency

### Small or medium city organization

The product can stay simple:

- mobile-friendly work updates
- role-based access
- project/team/task tracking
- blocker reporting
- operational dashboard

The system should not assume that every organization needs a huge enterprise suite.

---

## 15. Product customization principle

Keep the **core engine stable**.

Customize the **domain layer**.

### Stable core

- authentication
- users
- roles
- teams
- projects/jobs
- tasks/work
- status transitions
- audit history
- notifications
- analytics
- reports

### Industry-specific modules

Add what the organization actually needs.

Examples:

- manufacturing -> machine, shift, batch, quality, downtime
- automation -> site, panel, PLC, commissioning
- construction -> site, material, contractor, safety
- software -> sprint, repository, release, client approval
- logistics -> vehicle, route, shipment, delivery
- hospitality -> reservation, room, housekeeping, event

---

## 16. Success criteria

The project succeeds when a real organization can answer these questions without chasing people manually:

1. What work exists?
2. Who owns it?
3. What is happening now?
4. What is stuck?
5. Why is it stuck?
6. What is completed?
7. What is at risk?
8. Who needs to act?
9. What changed?
10. What evidence supports the management decision?

---

## 17. Long-term product direction

The long-term vision is:

`Operational System -> Operational Intelligence -> Industry-specific Intelligence`

First collect reliable events.

Then build deterministic analytics.

Then add AI on top of trustworthy data.

AI should eventually answer questions such as:

- "Which project needs attention?"
- "Why is this project delayed?"
- "Which blockers are recurring?"
- "Which teams are overloaded?"
- "What should the supervisor investigate today?"

The AI layer should be an interpretation layer, not the source of truth.

---

## 18. What you should be able to explain after studying this PRD

You should confidently explain:

> "I built a role-aware workforce execution and operational intelligence platform. It models organizations, teams, projects and tasks, lets workers update the work they actually own, records status transitions and work updates, derives project progress from task execution, and exposes that operational truth to team leaders, supervisors and owners. The architecture is intentionally reusable so the same execution engine can be customized for software agencies, automation companies, manufacturing/material organizations, field operations and other small or medium businesses."

That is the product in one paragraph.
