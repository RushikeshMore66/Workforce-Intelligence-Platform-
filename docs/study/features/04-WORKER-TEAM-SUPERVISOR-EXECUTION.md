# Case Study 04 — Worker, Team Leader and Supervisor Execution

## Goal

Understand why the product has multiple workforce roles.

## Worker

The worker owns execution.

Typical actions:

- view assigned work
- start work
- put work on hold
- provide hold reason
- mark work completed
- submit work updates

## Team Leader

The team leader owns team coordination.

Typical responsibility:

- understand team workload
- monitor task movement
- help resolve issues
- coordinate team execution

## Supervisor

The supervisor owns broader operational coordination.

Typical responsibility:

- manage scoped projects
- monitor multiple teams
- intervene in blockers
- manage worker/task scope
- control project execution

## Owner

The owner sees the organization.

Typical responsibility:

- organization-wide visibility
- project oversight
- workforce oversight
- analytics
- reporting
- strategic intelligence

## Why separate roles?

Because operational software should reflect authority.

A worker should not perform owner actions.

A supervisor should not automatically see every organization.

A team leader should not manage unrelated teams.

## Current worker experience

The `/my-work` workspace is intentionally simple.

The worker should not need a giant management dashboard.

They need:

- assigned work
- current state
- next legal actions
- work update field

## Core operational loop

```
Worker executes
      ↓
Worker updates task
      ↓
Task status changes
      ↓
Task transition is recorded
      ↓
Project progress changes
      ↓
Supervisor sees updated reality
```

## What I should be able to explain

> "The system mirrors the organization's chain of operational responsibility. Workers update execution, team leaders coordinate teams, supervisors coordinate projects, and owners see the organization."

## Industrial mapping examples

### Software agency

Worker = Developer

Team Leader = Tech Lead

Supervisor = Delivery Manager

Owner = Agency owner

### Automation agency

Worker = Automation Engineer

Team Leader = Site/Technical Lead

Supervisor = Project/Operations Manager

Owner = Founder

### Manufacturing

Worker = Operator/Technician

Team Leader = Shift/Line Lead

Supervisor = Production Supervisor

Owner = Plant/business owner

