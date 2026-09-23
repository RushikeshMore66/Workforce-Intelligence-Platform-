# Case Study 06 — Dashboard, Analytics, Reports and Intelligence

## Goal

Understand how raw operational events become management information.

## Data hierarchy

```
Tasks
Work Updates
Blockers
Transitions
Projects
Teams
Workers
      ↓
Aggregations
      ↓
Analytics
      ↓
Dashboard / Reports
      ↓
Intelligence
```

## Dashboard

The dashboard should answer:

> "What is happening across the organization?"

It displays summaries instead of requiring the owner to inspect every task.

## Analytics

Analytics are deterministic calculations.

Examples:

- completed tasks
- in-progress tasks
- workload
- worker metrics
- project delivery metrics
- team metrics
- cycle time

Analytics should be explainable from database records.

## Reports

Reports turn system data into repeatable management outputs.

Possible uses:

- daily operational report
- weekly project report
- monthly delivery report
- worker/team reports
- exports

## Intelligence

Intelligence should sit above analytics.

A deterministic system can say:

> "Project A is 42% complete."

An intelligence layer can eventually ask:

> "Why is Project A behind?"

Then AI can inspect:

- overdue tasks
- blockers
- hold reasons
- work updates
- deadline
- workload
- historical patterns

## Important AI principle

AI should not invent operational facts.

The database is the source of truth.

AI is the interpretation layer.

`Database truth -> deterministic analytics -> AI explanation/recommendation`

## What I should be able to explain

> "The platform first captures operational events, then calculates deterministic metrics, then exposes them through dashboards and reports. AI can later interpret those trusted signals."

