# Security Endpoint Audit

This document provides a comprehensive security inventory of all backend API endpoints, classifying authentication, authorization, and known risks.

## 1. Authentication (AUTH)

| Endpoint | Auth Required | Allowed Roles | Resource Scope | IDOR Risk | Mutation Risk |
|---|---|---|---|---|---|
| `POST /auth/login` | No (Public) | All | N/A | None | None |
| `GET /auth/me` | Yes | All | Current user profile | None | None |

## 2. Dashboard (DASHBOARD)

| Endpoint | Auth Required | Allowed Roles | Resource Scope | IDOR Risk | Mutation Risk |
|---|---|---|---|---|---|
| `GET /dashboard/metrics` | Yes | All | **Organization-wide** | None (aggregated) | None |
| `GET /dashboard/attention` | Yes | All | **Organization-wide** | None | None |
| `GET /dashboard/activities`| Yes | All | **Organization-wide** | None | None |

> **Risk Assessment:** The dashboard returns organizational metrics to all authenticated users. This is an intentional design choice reflecting a "shared dashboard" product philosophy. No PII is exposed, but broad business volume data (total projects, total tasks) is visible to workers.

## 3. Projects (PROJECTS)

| Endpoint | Auth Required | Allowed Roles | Resource Scope | IDOR Risk | Mutation Risk |
|---|---|---|---|---|---|
| `GET /projects` | Yes | All | **Assigned** (Team or Sup) | Mitigated by scope | None |
| `POST /projects` | Yes | OWNER, SUPERVISOR | N/A | N/A | Low (Role-gated) |
| `GET /projects/{id}` | Yes | All | **Assigned** | Mitigated by auth helper | None |
| `PATCH /projects/{id}` | Yes | OWNER, SUPERVISOR | **Assigned** | Mitigated by auth helper | Medium |
| `GET /projects/{id}/tasks` | Yes | All | **Assigned** | Mitigated by auth helper | None |
| `GET /projects/{id}/blockers` | Yes | All | **Assigned** | Mitigated by auth helper | None |
| `GET /projects/{id}/activities` | Yes | All | **Assigned** | Mitigated by auth helper | None |

## 4. Tasks (TASKS)

| Endpoint | Auth Required | Allowed Roles | Resource Scope | IDOR Risk | Mutation Risk |
|---|---|---|---|---|---|
| `GET /tasks/{id}` | Yes | All | **Assigned** | Mitigated by auth helper | None |
| `POST /tasks` | Yes | OWNER, SUP, LEADER | N/A | None | Medium |
| `PATCH /tasks/{id}` | Yes | All | **Assigned** | Mitigated by auth helper | Medium |
| `POST /tasks/{id}/updates` | Yes | All | **Assigned** | Mitigated by auth helper | Medium |

> **Note on Work Updates:** Authorization is tied to task access. Workers can only update their own assigned tasks. Supervisors and Team Leaders can post updates on tasks within their scope (e.g. on behalf of their team), per existing business requirements.

## 5. Blockers (BLOCKERS)

| Endpoint | Auth Required | Allowed Roles | Resource Scope | IDOR Risk | Mutation Risk |
|---|---|---|---|---|---|
| `GET /blockers` | Yes | All | **Assigned Projects** | Mitigated | None |
| `POST /blockers` | Yes | All | **Assigned Projects** | Mitigated | Medium |
| `PATCH /blockers/{id}` | Yes | All | **Assigned Projects** | Mitigated | Medium |

## 6. Workers (WORKERS)

| Endpoint | Auth Required | Allowed Roles | Resource Scope | IDOR Risk | Mutation Risk |
|---|---|---|---|---|---|
| `GET /workers` | Yes | All | **Assigned/Self** | Mitigated | None |
| `GET /workers/{id}` | Yes | All | **Assigned/Self** | Mitigated by auth helper | None |

## 7. Teams (TEAMS)

| Endpoint | Auth Required | Allowed Roles | Resource Scope | IDOR Risk | Mutation Risk |
|---|---|---|---|---|---|
| `GET /teams` | Yes | All | **Assigned/Own** | Mitigated | None |
| `GET /teams/{id}` | Yes | All | **Assigned/Own** | Mitigated by auth helper | None |

## 8. Supervisors (SUPERVISORS)

| Endpoint | Auth Required | Allowed Roles | Resource Scope | IDOR Risk | Mutation Risk |
|---|---|---|---|---|---|
| `GET /supervisors` | Yes | All | **Organization-wide** | None | None |
| `GET /supervisors/{id}`| Yes | All | **Organization-wide** | None | None |

> **Risk Assessment:** Supervisor profiles are visible organization-wide to facilitate project assignment drop-downs and UI references. This is an intentional design choice and exposes minimal data (name, email).

## 9. Notifications (NOTIFICATIONS)

| Endpoint | Auth Required | Allowed Roles | Resource Scope | IDOR Risk | Mutation Risk |
|---|---|---|---|---|---|
| `GET /notifications` | Yes | All | **Own Notifications** | Mitigated by DB query | None |
| `PATCH /notifications/{id}/read` | Yes | All | **Own Notifications** | Mitigated by auth helper | Low |
| `POST /notifications/read-all` | Yes | All | **Own Notifications** | Mitigated by DB query | Low |

## 10. Analytics (ANALYTICS)

| Endpoint | Auth Required | Allowed Roles | Resource Scope | IDOR Risk | Mutation Risk |
|---|---|---|---|---|---|
| `GET /analytics` | Yes | OWNER, SUPERVISOR| **Organization-wide** | None | None |

## Summary of IDOR Defenses
Every single resource endpoint (`/{id}`) enforces an access check via database relationships (e.g. `authorize_project_access`, `authorize_worker_access`). It is impossible to access a resource merely by knowing its UUID if it does not fall within the authenticated user's assigned scope.
