# Workforce Intelligence Platform — Production Readiness Audit

> **Scope:** Current `workflow-hardening` branch.
>
> **Purpose:** Track what must be fixed before calling the application production-ready.
>
> **Important:** This is an audit, not a claim that the application is already production-ready.

---

# 1. Current conclusion

**The system is NOT production-ready yet.**

The core architecture is present, but several product, security, data-integrity, and operational gaps remain.

The biggest gaps are:

1. No real in-application user provisioning.
2. No complete user profile management.
3. No account activation/deactivation lifecycle.
4. Authentication/session design needs production hardening.
5. Some backend authorization boundaries are broader than the frontend rules.
6. Analytics/reporting still contains stale or demo-oriented logic.
7. Several CRUD capabilities implied by permissions are not implemented.
8. Current tests contain references to the old task statuses.
9. Local database/credential material exists in the public repository and must be cleaned up.
10. Some frontend controls are visual placeholders rather than real settings/actions.
11. Several API clients and backend endpoints are not fully aligned.

---

# 2. P0 — Must fix before production

## P0.1 User provisioning

### Current problem

The repository contains `UserCreate`, but there is no registered users router/service in the application.

The backend currently registers routers for:

- auth
- dashboard
- projects
- workers
- supervisors
- teams
- tasks
- blockers
- analytics
- notifications
- reports
- report schedules

There is no `users` router.

### Consequence

New employees cannot be provisioned through the application.

The current demo environment relies on the seed process.

### Required solution

Create owner-controlled user provisioning:

`OWNER -> Create User -> Role -> Profile -> Team/Scope -> Login`

Role-specific profile creation must be transactional:

- SUPERVISOR -> Supervisor profile
- TEAM_LEADER -> TeamLeader profile
- WORKER -> Worker profile
- OWNER -> organization owner account

Also add:

- duplicate-email validation
- password policy
- audit event
- safe error response

---

## P0.2 User profile

### Current problem

`/settings` currently displays basic user information, but the profile is not an actual editable profile workflow.

The ProfileCard displays:

- name
- email
- role

The account fields are display-only.

The topbar "Profile" item does not lead to a dedicated working profile workflow.

### Required solution

Create a real profile API:

- GET current profile
- PATCH current profile
- change password

Suggested editable fields:

- name
- avatar initials/photo reference
- company/profile metadata where appropriate

Keep role changes restricted to authorized administration.

Email changes should have a controlled flow because identity is tied to the account.

---

## P0.3 Account lifecycle

### Current problem

The User model does not have a dedicated `is_active` account state.

Worker operational status:

- ACTIVE
- ON_LEAVE
- UNAVAILABLE

is not the same thing as an account being allowed to authenticate.

### Required solution

Add account lifecycle:

`ACTIVE -> SUSPENDED/DEACTIVATED`

Authentication must reject inactive accounts.

Owner/admin actions:

- activate
- deactivate
- optionally force password reset

Operational worker status stays separate.

---

## P0.4 Session security

Current frontend authentication stores the bearer token in browser localStorage.

For an internet-facing production SaaS, review moving authentication to a safer cookie-based session strategy, such as Secure + HttpOnly + appropriate SameSite cookies, or formally document and mitigate the risks of browser token storage.

Authentication and authorization are separate concerns; production route protection must cover both. citeturn945767search0turn945767search3

Also decide whether the system needs:

- refresh sessions
- session revocation
- logout-all-sessions
- password-change token invalidation

---

## P0.5 Credential and repository hygiene

The public repository currently contains:

- committed local SQLite database files
- credential material in project documentation
- demo credentials in seed/documentation

This must be cleaned before production.

### Required actions

1. Remove local database files from Git history/current tree.
2. Remove credentials from documentation.
3. Rotate any credential that may have been real or reused.
4. Keep secrets only in environment/secret management.
5. Ensure seed/demo credentials cannot accidentally be used in production.

The seed script must be explicitly development/test-only.

---

## P0.6 Backend authorization mismatches

Some frontend pages are restricted more tightly than their backend endpoints.

Example:

The frontend treats Supervisors as owner-only for the Supervisors section, but the backend supervisor GET endpoints currently require only authentication.

Similarly, schedule endpoints use a broad organization permission while the UI presents them as owner-only.

Authorization must be enforced in the backend because UI hiding is not a security boundary.

---

## P0.7 Analytics data correctness

There are multiple analytics layers.

Some are real SQL-derived analytics.

However, `AnalyticsService.get_analytics_data()` currently returns hard-coded demonstration data.

That is not acceptable for a production analytics screen.

### Required solution

Every production analytics value must have a traceable source:

`Database -> deterministic query -> analytics response -> UI`

No hard-coded production numbers.

---

## P0.8 Old task status references

The canonical task status is now:

- PLANNED
- IN_PROGRESS
- ON_HOLD
- COMPLETED
- CANCELLED

But several backend services/tests/frontend labels still reference the older:

- TODO
- BLOCKED
- To Do
- Blocked

Known areas requiring cleanup include:

- dashboard service
- team analytics
- worker analytics
- organization analytics
- report service
- tests
- frontend analytics labels

The system must use one canonical vocabulary.

---

# 3. P1 — Required for a complete usable product

## P1.1 Complete administration

Permissions imply capabilities such as:

- supervisor create/update/deactivate
- worker create/update/deactivate
- team create/update/delete
- project assignment
- task delete

but several corresponding endpoints are not currently present.

Implement only the capabilities that are truly part of the product contract, then make permissions match actual endpoints.

---

## P1.2 Role-specific workspaces

Required operational surfaces:

### Worker

`My Work`

- assigned tasks
- status changes
- work updates
- blockers
- personal workload

### Team Leader

`Team Work`

- team tasks
- worker workload
- blockers
- execution coordination

### Supervisor

`Supervisor Control`

- projects
- teams
- overdue work
- on-hold work
- workforce workload
- intervention actions

### Owner

`Executive Operations`

- organization status
- project health
- workforce
- analytics
- reports
- intelligence

---

## P1.3 Profile/context completeness

Current `/auth/me` returns basic identity.

Production UX should be able to obtain the user's operational context cleanly.

For example:

`User -> Role -> Profile -> Team -> Supervisor -> Permissions`

Avoid frontend hacks such as discovering a worker by matching email.

---

## P1.4 Data integrity rules

Enforce organizational consistency.

Examples:

- worker.team matches worker's leadership/supervisor scope
- worker.team_leader_id belongs to worker.team
- worker.supervisor_id matches the team's supervisor where required
- task.team belongs to project
- assigned worker belongs to task team
- active project belongs to worker's permitted project scope

The database and service layer should prevent impossible organizational states.

---

## P1.5 Project workflow audit

Task transitions have a dedicated transition record.

Project lifecycle changes currently use project activities.

For stronger production auditing, consider a dedicated project transition history with:

- previous status
- next status
- changed by
- timestamp
- reason

---

## P1.6 Notifications

Notification CRUD exists, but production readiness should verify that important events actually create notifications.

Examples:

- task put on hold
- blocker reported
- deadline approaching
- project risk detected
- assignment changed

A notification system is useful only when the operational events are connected to it.

---

## P1.7 Search

The topbar search field currently behaves visually like a search control.

Production behavior needs to define:

- what is searchable
- who can search it
- scope restrictions
- result ranking
- navigation

---

## P1.8 Settings

Current notification toggles are visual placeholders.

Production settings must either:

- persist real preferences, or
- be removed until implemented.

A control should not look active if it does not change system behavior.

---

# 4. P2 — Reliability and operations

## P2.1 Rate limiting

The configuration contains a rate-limit placeholder but no enforced limiter.

At minimum, protect:

- login
- password operations
- other abuse-sensitive endpoints

---

## P2.2 Metrics security

The Prometheus metrics endpoint currently has no authentication check.

For production infrastructure:

- keep metrics private/internal, or
- protect it through network controls/authentication

Do not expose infrastructure metrics publicly without a reason.

---

## P2.3 API documentation exposure

Swagger/ReDoc are useful during development.

Production policy should decide whether they are:

- disabled
- protected
- restricted to internal access

---

## P2.4 Trusted hosts

The application has TrustedHost support, but production configuration should require explicit trusted-host configuration rather than relying on a development default.

---

## P2.5 CORS

Development origins are currently configured.

Production must use the real frontend origins only.

Never broaden production CORS just to "make it work."

---

## P2.6 Report storage

Report outputs are stored on the filesystem.

This can work for a single local instance, but production architecture should define durable storage and cleanup behavior if the application becomes multi-instance.

---

## P2.7 Scheduler

The project contains a report scheduler.

Production must ensure only one scheduler process performs scheduled jobs, rather than accidentally running duplicate schedulers across API workers.

---

# 5. P2 — Frontend reliability

Check every route for:

- loading state
- refresh state
- empty state
- 401 state
- 403 state
- 404 state
- 500/network failure
- stale data after mutation
- duplicate submit protection

Existing project-list flicker work should be regression-tested after the production cleanup.

---

# 6. API contract consistency

Review every frontend API function against a real backend endpoint.

Known examples requiring attention:

- worker task retrieval path
- team filtering parameters
- supervisor filtering
- project/worker filter parameters
- team task retrieval

Do not keep frontend functions that call endpoints the backend does not implement.

---

# 7. Testing gate

Before production:

## Backend

Run:

`pytest -v`

Verify:

- auth
- user provisioning
- profile
- account lifecycle
- RBAC
- object-level authorization
- task workflow
- project workflow
- progress
- blockers
- notifications
- analytics
- reports
- scheduler

## Frontend

Run:

`npm run lint`

and:

`npm run build`

Then manually test every role.

---

# 8. End-to-end role test matrix

## Owner

- login
- profile
- create supervisor
- create team
- create worker
- create project
- assign project/team/work
- view organization analytics
- export report
- deactivate user

## Supervisor

- login
- profile
- see only own scope
- see assigned projects
- see own teams
- manage permitted work
- review blockers
- change permitted project status

## Team Leader

- login
- profile
- see own team
- see team workers
- see team tasks
- coordinate work
- view team analytics where allowed

## Worker

- login
- profile
- see own work
- start task
- put task on hold with reason
- add work update
- complete task
- see own relevant information only

---

# 9. Production readiness definition

Do not call the product production-ready because:

- the UI looks polished
- login works
- the dashboard loads
- API returns 200
- seed data looks realistic

Call it production-ready only when:

`Identity`

`Authorization`

`Data Integrity`

`Workflow correctness`

`Real Data`

`Error Handling`

`Testing`

`Security`

`Operational Reliability`

all pass the defined acceptance tests.

---

# 10. Recommended fix sequence

### Phase A — Identity

1. User provisioning
2. User profile
3. Account activation/deactivation
4. Password change/reset strategy
5. Session hardening

### Phase B — Authorization

6. Backend endpoint role enforcement
7. Scope policies
8. Role-specific administration

### Phase C — Data correctness

9. Remove old task status references
10. Fix analytics
11. Fix reports
12. Fix data-integrity invariants
13. Recalculate seed/demo derived values

### Phase D — Product completeness

14. Supervisor workspace
15. Team leader workspace
16. Worker/profile improvements
17. notifications
18. search
19. real settings

### Phase E — Production gate

20. Migration test
21. full pytest
22. lint
23. production build
24. end-to-end role testing
25. security review
26. repository/secret cleanup
27. backup/restore verification

Only after this gate should deployment be considered.

---

# 11. Product principle

The production version should stay aligned with the original mission:

> **Solve real operational problems through the people doing the work.**

Every production feature should answer:

> **What operational problem does this remove?**
