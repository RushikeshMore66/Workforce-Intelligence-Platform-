# Authorization Matrix — Phase 5

All endpoints require `Authorization: Bearer <token>` unless marked **Public**.

## Legend
- ✅ Allowed
- ❌ Forbidden (403)
- 🚫 Unauthenticated (401)
- ⬛ Not applicable / no data to return
- ⚠️ Scoped (allowed but filtered to accessible resources only)

---

## AUTH

| Endpoint | OWNER | SUPERVISOR | TEAM_LEADER | WORKER | No Token |
|---|---|---|---|---|---|
| `POST /auth/login` | ✅ | ✅ | ✅ | ✅ | ✅ Public |
| `GET /auth/me` | ✅ | ✅ | ✅ | ✅ | 🚫 401 |

---

## DASHBOARD

| Endpoint | OWNER | SUPERVISOR | TEAM_LEADER | WORKER | No Token |
|---|---|---|---|---|---|
| `GET /dashboard/metrics` | ✅ All | ✅ All | ✅ All | ✅ All | 🚫 401 |
| `GET /dashboard/attention` | ✅ All | ✅ All | ✅ All | ✅ All | 🚫 401 |
| `GET /dashboard/activities` | ✅ All | ✅ All | ✅ All | ✅ All | 🚫 401 |

> **Note:** Dashboard is intentionally organization-wide (shared org intelligence dashboard). No role scoping applied.

---

## PROJECTS

| Endpoint | OWNER | SUPERVISOR | TEAM_LEADER | WORKER | No Token |
|---|---|---|---|---|---|
| `GET /projects` | ✅ All | ⚠️ Assigned only | ⚠️ Team's projects | ⚠️ Team's projects | 🚫 401 |
| `GET /projects/{id}` | ✅ Any | ⚠️ Own assignment | ⚠️ Team's project | ⚠️ Team's project | 🚫 401 |
| `POST /projects` | ✅ | ✅ | ❌ 403 | ❌ 403 | 🚫 401 |
| `PATCH /projects/{id}` | ✅ Any | ⚠️ Own assignment only | ❌ 403 | ❌ 403 | 🚫 401 |
| `GET /projects/{id}/tasks` | ✅ | ⚠️ | ⚠️ | ⚠️ | 🚫 401 |
| `GET /projects/{id}/blockers` | ✅ | ⚠️ | ⚠️ | ⚠️ | 🚫 401 |
| `GET /projects/{id}/activities` | ✅ | ⚠️ | ⚠️ | ⚠️ | 🚫 401 |

---

## WORKERS

| Endpoint | OWNER | SUPERVISOR | TEAM_LEADER | WORKER | No Token |
|---|---|---|---|---|---|
| `GET /workers` | ✅ All | ⚠️ Supervised workers | ⚠️ Own team workers | ⚠️ Self only | 🚫 401 |
| `GET /workers/{id}` | ✅ Any | ⚠️ Supervised workers | ⚠️ Own team worker | ⚠️ Self only | 🚫 401 |

---

## TEAMS

| Endpoint | OWNER | SUPERVISOR | TEAM_LEADER | WORKER | No Token |
|---|---|---|---|---|---|
| `GET /teams` | ✅ All | ⚠️ Assigned teams | ⚠️ Own team | ⚠️ Own team | 🚫 401 |
| `GET /teams/{id}` | ✅ Any | ⚠️ Own assignment | ⚠️ Own team | ⚠️ Own team | 🚫 401 |
| `GET /teams/{id}/workers` | ✅ | ⚠️ | ⚠️ | ⚠️ | 🚫 401 |

---

## SUPERVISORS

| Endpoint | OWNER | SUPERVISOR | TEAM_LEADER | WORKER | No Token |
|---|---|---|---|---|---|
| `GET /supervisors` | ✅ | ✅ | ✅ | ✅ | 🚫 401 |
| `GET /supervisors/{id}` | ✅ | ✅ | ✅ | ✅ | 🚫 401 |

> **Intentionally permissive:** Supervisor profiles are referenced by all roles in project/team UIs. No sensitive data is exposed.

---

## TASKS

| Endpoint | OWNER | SUPERVISOR | TEAM_LEADER | WORKER | No Token |
|---|---|---|---|---|---|
| `GET /tasks/{id}` | ✅ | ⚠️ Project scope | ⚠️ Team scope | ⚠️ Own tasks | 🚫 401 |
| `POST /tasks` | ✅ | ✅ | ✅ | ❌ 403 | 🚫 401 |
| `PATCH /tasks/{id}` | ✅ | ⚠️ Project scope | ⚠️ Team scope | ⚠️ Own tasks | 🚫 401 |
| `POST /tasks/{id}/updates` | ✅ | ⚠️ Project scope | ⚠️ Team scope | ⚠️ Own tasks | 🚫 401 |

---

## BLOCKERS

| Endpoint | OWNER | SUPERVISOR | TEAM_LEADER | WORKER | No Token |
|---|---|---|---|---|---|
| `GET /blockers` | ✅ All | ⚠️ Own projects | ⚠️ Team's projects | ⚠️ Team's projects | 🚫 401 |
| `POST /blockers` | ✅ | ⚠️ Own projects | ⚠️ Team's projects | ⚠️ Team's projects | 🚫 401 |
| `PATCH /blockers/{id}` | ✅ | ⚠️ Own projects | ⚠️ Team's projects | ⚠️ Team's projects | 🚫 401 |

---

## NOTIFICATIONS

| Endpoint | OWNER | SUPERVISOR | TEAM_LEADER | WORKER | No Token |
|---|---|---|---|---|---|
| `GET /notifications` | ✅ Own | ✅ Own | ✅ Own | ✅ Own | 🚫 401 |
| `PATCH /notifications/{id}/read` | ✅ Own | ✅ Own | ✅ Own | ✅ Own | 🚫 401 |
| `POST /notifications/read-all` | ✅ Own | ✅ Own | ✅ Own | ✅ Own | 🚫 401 |

> Notification endpoints always return only the authenticated user's own notifications. IDOR fix applied to `PATCH /{id}/read`.

---

## ANALYTICS

| Endpoint | OWNER | SUPERVISOR | TEAM_LEADER | WORKER | No Token |
|---|---|---|---|---|---|
| `GET /analytics` | ✅ | ✅ | ❌ 403 | ❌ 403 | 🚫 401 |
