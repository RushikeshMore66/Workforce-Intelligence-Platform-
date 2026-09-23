# Case Study 07 — Customizing the Platform for Real Organizations

## Goal

Understand how the same core system can become different products without rebuilding the entire platform.

## The architecture has two layers

### Core engine

Keep stable:

- authentication
- RBAC
- users
- teams
- projects/jobs
- tasks/work
- workflows
- audit events
- notifications
- analytics
- reports

### Industry adapter

Change/customize:

- terminology
- extra entities
- workflow rules
- dashboards
- metrics
- forms
- alerts
- domain-specific intelligence

---

# Case A — Software agency

### Mapping

Project = Client delivery

Team = Development/design team

Task = development task

Worker = developer/designer/tester

Blocker = client approval / dependency / environment issue

### Extensions

Add:

- sprint
- repository
- release
- deployment
- client approval
- bug severity

---

# Case B — Automation agency

### Mapping

Project = Automation project

Task = engineering activity

Worker = automation engineer

Supervisor = project/operations manager

### Example tasks

- electrical design
- panel fabrication
- PLC programming
- HMI configuration
- installation
- commissioning
- customer testing

### Extensions

Add:

- site
- machine
- PLC
- panel
- commissioning stage
- client acceptance

---

# Case C — Manufacturing/material organization

### Mapping

Project/job = production order or customer job

Task = production step

Worker = operator/technician

Supervisor = production supervisor

### Example tasks

- material preparation
- machining
- inspection
- finishing
- packing
- dispatch

### Extensions

Add:

- machine
- shift
- batch
- quantity
- rejection
- downtime
- quality inspection

---

# Case D — Field service

Project/job = customer service job

Task = service step

Worker = field technician

Supervisor = service manager

Extensions:

- site
- equipment
- travel
- spare parts
- customer sign-off
- SLA

---

# Case E — Small or medium city business

Do not make the system unnecessarily complicated.

Start with:

- login
- teams
- jobs/projects
- tasks
- worker updates
- blockers
- dashboard
- reports

Only add modules when the real organization needs them.

## Customization rule

Do not ask:

> "What cool feature can we add?"

Ask:

> "What operational problem does this organization repeatedly face?"

Then map the problem to:

`Entity -> Workflow -> Event -> Metric -> Action`

That is the core of the product philosophy.

---

## Example

Problem:

"Owner finds out about material shortages too late."

System design:

Material requirement
-> task
-> blocker
-> blocker reason
-> notification
-> supervisor attention
-> dashboard

That is a real industrial use case.

---

## What I should be able to explain

> "I am not building a separate application from scratch for every industry. I am building a reusable operational execution engine and then adapting the domain model, workflows and intelligence layer for each organization."
