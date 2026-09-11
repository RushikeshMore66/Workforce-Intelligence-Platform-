"""
Tests for Phase 7.14 Reports Foundation.

Coverage:
1. RBAC for every endpoint
2. Empty/zero-safe metrics
3. Project scoping
4. Worker ownership
5. Team authorization
6. Authorship classification
7. Missing transition history
8. Pagination
9. Activity filters
10. Date boundaries
"""

from datetime import date, datetime, timedelta

import pytest

from app.auth.jwt import create_jwt_token
from app.models.project import Project, ProjectHealthEnum, ProjectStatusEnum
from app.models.task import Task, TaskStatusEnum, TaskTransition, WorkUpdate
from app.models.team import Team, team_projects
from app.models.user import (
    Supervisor,
    TeamLeader,
    User,
    UserRoleEnum,
    Worker,
    WorkerStatusEnum,
)


# ─── Helpers ─────────────────────────────────────────────────────────────────


def auth(user_id: str, role: UserRoleEnum) -> dict:
    token = create_jwt_token(user_id, role.value).access_token
    return {"Authorization": f"Bearer {token}"}


# ─── Shared fixture ───────────────────────────────────────────────────────────


@pytest.fixture
def report_data(db_session):
    """
    Stable, isolated dataset for report tests.
    Two teams, three workers, two projects, tasks with transitions and work updates.
    """
    # Wipe state
    for model in [TaskTransition, WorkUpdate, Task, team_projects, Project, Worker,
                  TeamLeader, Supervisor, Team]:
        db_session.query(model).delete()
    db_session.query(User).filter(User.id != "usr-test-owner").delete()
    db_session.commit()

    # Users
    sup_u = User(id="rp-sup-u", name="Sup", email="rp-sup@x.com", hashed_password="h",
                 role=UserRoleEnum.SUPERVISOR, avatar_initials="SU")
    tl_u  = User(id="rp-tl-u",  name="TL",  email="rp-tl@x.com",  hashed_password="h",
                 role=UserRoleEnum.TEAM_LEADER, avatar_initials="TL")
    w1_u  = User(id="rp-w1-u",  name="Alice", email="rp-w1@x.com", hashed_password="h",
                 role=UserRoleEnum.WORKER, avatar_initials="AL")
    w2_u  = User(id="rp-w2-u",  name="Bob",   email="rp-w2@x.com", hashed_password="h",
                 role=UserRoleEnum.WORKER, avatar_initials="BO")
    w3_u  = User(id="rp-w3-u",  name="Carol", email="rp-w3@x.com", hashed_password="h",
                 role=UserRoleEnum.WORKER, avatar_initials="CA")
    db_session.add_all([sup_u, tl_u, w1_u, w2_u, w3_u])
    db_session.commit()

    sup = Supervisor(id="rp-sup", user_id="rp-sup-u")
    db_session.add(sup)
    db_session.commit()

    team1 = Team(id="rp-team1", name="Alpha Team", supervisor_id="rp-sup")
    team2 = Team(id="rp-team2", name="Beta Team",  supervisor_id="rp-sup")
    db_session.add_all([team1, team2])
    db_session.commit()

    tl = TeamLeader(id="rp-tl", user_id="rp-tl-u", team_id="rp-team1")
    db_session.add(tl)
    db_session.commit()

    w1 = Worker(id="rp-w1", user_id="rp-w1-u", role="Dev", team_id="rp-team1",
                status=WorkerStatusEnum.ACTIVE)
    w2 = Worker(id="rp-w2", user_id="rp-w2-u", role="QA",  team_id="rp-team1",
                status=WorkerStatusEnum.ON_LEAVE)
    w3 = Worker(id="rp-w3", user_id="rp-w3-u", role="Dev", team_id="rp-team2",
                status=WorkerStatusEnum.ACTIVE)
    db_session.add_all([w1, w2, w3])
    db_session.commit()

    today = date.today()
    p1 = Project(id="rp-p1", name="Project Alpha", client="Client A",
                 start_date=today - timedelta(days=60), deadline=today + timedelta(days=30),
                 status=ProjectStatusEnum.ACTIVE, health=ProjectHealthEnum.ON_TRACK)
    p2 = Project(id="rp-p2", name="Project Beta", client="Client B",
                 start_date=today - timedelta(days=30), deadline=today + timedelta(days=60),
                 status=ProjectStatusEnum.PLANNED, health=ProjectHealthEnum.DELAYED)
    db_session.add_all([p1, p2])
    db_session.commit()

    # p1 assigned to team1
    db_session.execute(team_projects.insert().values(team_id="rp-team1", project_id="rp-p1"))
    db_session.commit()

    now = datetime.utcnow()

    # Tasks
    # t1: COMPLETED, w1, p1 — has valid cycle time (4h)
    t1 = Task(id="rp-t1", project_id="rp-p1", title="Task 1", assignee_id="rp-w1",
              status=TaskStatusEnum.COMPLETED, due_date=today + timedelta(days=5))
    # t2: BLOCKED, w2, p1, overdue
    t2 = Task(id="rp-t2", project_id="rp-p1", title="Task 2", assignee_id="rp-w2",
              status=TaskStatusEnum.BLOCKED, due_date=today - timedelta(days=3))
    # t3: IN_PROGRESS, unassigned, p1
    t3 = Task(id="rp-t3", project_id="rp-p1", title="Task 3", assignee_id=None,
              status=TaskStatusEnum.IN_PROGRESS, due_date=today + timedelta(days=10))
    # t4: COMPLETED, w3, p2 — no valid transition history
    t4 = Task(id="rp-t4", project_id="rp-p2", title="Task 4", assignee_id="rp-w3",
              status=TaskStatusEnum.COMPLETED, due_date=today + timedelta(days=1))
    db_session.add_all([t1, t2, t3, t4])
    db_session.commit()

    # Transitions — t1 has valid history; t4 does NOT (no TODO→IN_PROGRESS)
    tr1 = TaskTransition(id="rp-tr1", task_id="rp-t1",
                         from_status=TaskStatusEnum.TODO,
                         to_status=TaskStatusEnum.IN_PROGRESS,
                         timestamp=now - timedelta(hours=6))
    tr2 = TaskTransition(id="rp-tr2", task_id="rp-t1",
                         from_status=TaskStatusEnum.IN_PROGRESS,
                         to_status=TaskStatusEnum.COMPLETED,
                         timestamp=now - timedelta(hours=2))
    # t4: skip directly to COMPLETED — no valid start transition
    tr3 = TaskTransition(id="rp-tr3", task_id="rp-t4",
                         from_status=None,
                         to_status=TaskStatusEnum.COMPLETED,
                         timestamp=now - timedelta(hours=1))
    db_session.add_all([tr1, tr2, tr3])
    db_session.commit()

    # WorkUpdates
    # wu1: worker-authored by w1 (rp-w1-u == created_by)
    wu1 = WorkUpdate(id="rp-wu1", task_id="rp-t1", worker_id="rp-w1",
                     created_by_user_id="rp-w1-u", description="Worker note",
                     timestamp=now - timedelta(hours=5))
    # wu2: management-authored by sup
    wu2 = WorkUpdate(id="rp-wu2", task_id="rp-t1", worker_id="rp-w1",
                     created_by_user_id="rp-sup-u", description="Sup note",
                     timestamp=now - timedelta(hours=4))
    # wu3: NULL created_by — legacy/unknown
    wu3 = WorkUpdate(id="rp-wu3", task_id="rp-t2", worker_id="rp-w2",
                     created_by_user_id=None, description="Old note",
                     timestamp=now - timedelta(days=40))
    # wu4: worker-authored by w3 on p2
    wu4 = WorkUpdate(id="rp-wu4", task_id="rp-t4", worker_id="rp-w3",
                     created_by_user_id="rp-w3-u", description="W3 note",
                     timestamp=now - timedelta(hours=2))
    db_session.add_all([wu1, wu2, wu3, wu4])
    db_session.commit()


# ─── Organization report ──────────────────────────────────────────────────────


def test_org_report_owner_allowed(client, report_data):
    resp = client.get("/api/v1/reports/organization",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    data = resp.json()
    assert data["metadata"]["report_type"] == "organization"


def test_org_report_supervisor_forbidden(client, report_data):
    resp = client.get("/api/v1/reports/organization",
                      headers=auth("rp-sup-u", UserRoleEnum.SUPERVISOR))
    assert resp.status_code == 403


def test_org_report_worker_forbidden(client, report_data):
    resp = client.get("/api/v1/reports/organization",
                      headers=auth("rp-w1-u", UserRoleEnum.WORKER))
    assert resp.status_code == 403


def test_org_report_team_leader_forbidden(client, report_data):
    resp = client.get("/api/v1/reports/organization",
                      headers=auth("rp-tl-u", UserRoleEnum.TEAM_LEADER))
    assert resp.status_code == 403


def test_org_report_metrics(client, report_data):
    resp = client.get("/api/v1/reports/organization",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    d = resp.json()
    assert d["total_workers"] == 3
    assert d["active_workers"] == 2
    assert d["total_teams"] == 2
    assert d["total_projects"] == 2
    assert d["active_projects"] == 1
    assert d["total_tasks"] == 4
    assert d["completed_tasks"] == 2
    assert abs(d["completion_rate"] - 0.5) < 1e-9
    assert d["overdue_tasks"] == 1   # t2
    assert d["blocked_tasks"] == 1   # t2
    assert d["unassigned_tasks"] == 1  # t3


def test_org_report_zero_safe(client, db_session):
    """Zero-data state must not crash and must return 0.0 for rates."""
    for model in [TaskTransition, WorkUpdate, Task, team_projects, Project,
                  Worker, TeamLeader, Supervisor, Team]:
        db_session.query(model).delete()
    db_session.query(User).filter(User.id != "usr-test-owner").delete()
    db_session.commit()

    resp = client.get("/api/v1/reports/organization",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    d = resp.json()
    assert d["total_workers"] == 0
    assert d["completion_rate"] == 0.0
    assert d["overdue_tasks"] == 0


# ─── Project report ───────────────────────────────────────────────────────────


def test_project_report_owner(client, report_data):
    resp = client.get("/api/v1/reports/projects/rp-p1",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    d = resp.json()
    assert d["project_id"] == "rp-p1"
    assert d["project_name"] == "Project Alpha"
    assert d["total_tasks"] == 3
    assert d["completed_tasks"] == 1
    assert d["blocked_tasks"] == 1
    assert d["overdue_tasks"] == 1    # t2
    assert d["unassigned_tasks"] == 1  # t3
    # Authorship: wu1=worker, wu2=management, wu3=unknown (null)
    assert d["total_updates"] == 3
    assert d["worker_authored_updates"] == 1
    assert d["management_authored_updates"] == 1
    assert abs(d["completion_rate"] - 1 / 3) < 1e-9
    assert d["average_cycle_time_hours"] == pytest.approx(4.0, abs=0.01)


def test_project_report_worker_wrong_team_forbidden(client, report_data):
    """Worker in team2 cannot access p1 (assigned to team1)."""
    resp = client.get("/api/v1/reports/projects/rp-p1",
                      headers=auth("rp-w3-u", UserRoleEnum.WORKER))
    assert resp.status_code == 403


def test_project_report_not_found(client, report_data):
    resp = client.get("/api/v1/reports/projects/nonexistent",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 404


def test_project_report_missing_transition_history(client, report_data):
    """p2 task t4 has no TODO→IN_PROGRESS transition — cycle time must be None."""
    resp = client.get("/api/v1/reports/projects/rp-p2",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    d = resp.json()
    assert d["completed_tasks"] == 1
    assert d["average_cycle_time_hours"] is None


def test_project_report_zero_tasks(client, db_session, report_data):
    """Project with no tasks — completion_rate 0.0, cycle time None."""
    # Create an isolated empty project
    from app.models.project import ProjectStatusEnum, ProjectHealthEnum
    ep = Project(id="rp-empty", name="Empty Project", client="C",
                 start_date=date.today(), deadline=date.today() + timedelta(days=1),
                 status=ProjectStatusEnum.PLANNED, health=ProjectHealthEnum.ON_TRACK)
    db_session.add(ep)
    db_session.commit()
    resp = client.get("/api/v1/reports/projects/rp-empty",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    d = resp.json()
    assert d["total_tasks"] == 0
    assert d["completion_rate"] == 0.0
    assert d["average_cycle_time_hours"] is None


# ─── Worker report ────────────────────────────────────────────────────────────


def test_worker_report_owner(client, report_data):
    resp = client.get("/api/v1/reports/workers/rp-w1",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    d = resp.json()
    assert d["worker_id"] == "rp-w1"
    assert d["worker_name"] == "Alice"
    assert d["total_tasks"] == 1
    assert d["completed_tasks"] == 1
    assert d["completion_rate"] == 1.0
    assert d["total_updates"] == 2       # wu1 + wu2
    assert d["worker_authored_updates"] == 1
    assert d["management_authored_updates"] == 1
    assert d["average_cycle_time_hours"] == pytest.approx(4.0, abs=0.01)


def test_worker_report_self(client, report_data):
    """Workers can access their own report."""
    resp = client.get("/api/v1/reports/workers/rp-w1",
                      headers=auth("rp-w1-u", UserRoleEnum.WORKER))
    assert resp.status_code == 200


def test_worker_report_other_worker_forbidden(client, report_data):
    """Workers cannot access another worker's report."""
    resp = client.get("/api/v1/reports/workers/rp-w2",
                      headers=auth("rp-w1-u", UserRoleEnum.WORKER))
    assert resp.status_code == 403


def test_worker_report_authorship_classification(client, report_data):
    """w2 has 1 update with NULL created_by — should be excluded from both categories."""
    resp = client.get("/api/v1/reports/workers/rp-w2",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    d = resp.json()
    assert d["total_updates"] == 1
    assert d["worker_authored_updates"] == 0
    assert d["management_authored_updates"] == 0


def test_worker_report_zero_safe(client, report_data):
    """w3 on p2 has no overdue tasks; test zero path for cycle time."""
    resp = client.get("/api/v1/reports/workers/rp-w3",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    d = resp.json()
    assert d["completion_rate"] == 1.0  # 1/1 completed
    assert d["average_cycle_time_hours"] is None  # no valid start transition


# ─── Team report ─────────────────────────────────────────────────────────────


def test_team_report_owner(client, report_data):
    resp = client.get("/api/v1/reports/teams/rp-team1",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    d = resp.json()
    assert d["team_id"] == "rp-team1"
    assert d["team_name"] == "Alpha Team"
    assert d["total_workers"] == 2
    assert d["active_workers"] == 1
    # Tasks assigned to team1 workers (w1, w2): t1, t2
    assert d["total_tasks"] == 2
    assert d["completed_tasks"] == 1
    assert d["blocked_tasks"] == 1
    assert d["overdue_tasks"] == 1
    assert d["total_updates"] == 3   # wu1+wu2 (w1) + wu3 (w2)
    assert d["worker_authored_updates"] == 1
    assert d["management_authored_updates"] == 1
    assert d["average_cycle_time_hours"] == pytest.approx(4.0, abs=0.01)


def test_team_report_team_leader_own(client, report_data):
    """Team leader can access their own team's report."""
    resp = client.get("/api/v1/reports/teams/rp-team1",
                      headers=auth("rp-tl-u", UserRoleEnum.TEAM_LEADER))
    assert resp.status_code == 200


def test_team_report_worker_own_team_allowed(client, report_data):
    """Workers can access their own team's report."""
    resp = client.get("/api/v1/reports/teams/rp-team1",
                      headers=auth("rp-w1-u", UserRoleEnum.WORKER))
    assert resp.status_code == 200


def test_team_report_worker_other_team_forbidden(client, report_data):
    """Workers cannot access a different team's report."""
    # w1 is in team1; team2 should be 403
    resp = client.get("/api/v1/reports/teams/rp-team2",
                      headers=auth("rp-w1-u", UserRoleEnum.WORKER))
    assert resp.status_code == 403


def test_team_report_not_found(client, report_data):
    resp = client.get("/api/v1/reports/teams/nonexistent",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 404


def test_team_report_missing_transition_history(client, report_data):
    """team2 / w3 has no valid TODO→IN_PROGRESS — cycle time must be None."""
    resp = client.get("/api/v1/reports/teams/rp-team2",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    d = resp.json()
    assert d["average_cycle_time_hours"] is None


# ─── Activity report ──────────────────────────────────────────────────────────


def test_activity_report_owner_all(client, report_data):
    resp = client.get("/api/v1/reports/activity",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    d = resp.json()
    assert d["total"] == 4  # wu1-wu4
    assert len(d["items"]) == 4
    # Newest first
    timestamps = [item["timestamp"] for item in d["items"]]
    assert timestamps == sorted(timestamps, reverse=True)


def test_activity_report_filter_worker(client, report_data):
    resp = client.get("/api/v1/reports/activity?worker_id=rp-w1",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    d = resp.json()
    assert d["total"] == 2  # wu1, wu2
    assert all(item["worker_id"] == "rp-w1" for item in d["items"])


def test_activity_report_filter_project(client, report_data):
    resp = client.get("/api/v1/reports/activity?project_id=rp-p2",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    d = resp.json()
    assert d["total"] == 1  # wu4
    assert d["items"][0]["project_id"] == "rp-p2"


def test_activity_report_filter_team(client, report_data):
    resp = client.get("/api/v1/reports/activity?team_id=rp-team2",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    d = resp.json()
    assert d["total"] == 1  # wu4 (w3 in team2)


def test_activity_report_pagination(client, report_data):
    resp = client.get("/api/v1/reports/activity?limit=2&offset=0",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    d = resp.json()
    assert d["total"] == 4
    assert len(d["items"]) == 2
    assert d["limit"] == 2
    assert d["offset"] == 0

    resp2 = client.get("/api/v1/reports/activity?limit=2&offset=2",
                       headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    d2 = resp2.json()
    assert len(d2["items"]) == 2
    # Pages should not overlap
    ids_p1 = {i["update_id"] for i in d["items"]}
    ids_p2 = {i["update_id"] for i in d2["items"]}
    assert ids_p1.isdisjoint(ids_p2)


def test_activity_report_limit_capped_at_100(client, report_data):
    resp = client.get("/api/v1/reports/activity?limit=999",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    # FastAPI query validator enforces le=100
    assert resp.status_code == 422


def test_activity_report_authorship_labels(client, report_data):
    resp = client.get("/api/v1/reports/activity?worker_id=rp-w1",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    items = {i["update_id"]: i for i in resp.json()["items"]}
    assert items["rp-wu1"]["authorship"] == "worker"
    assert items["rp-wu2"]["authorship"] == "management"


def test_activity_report_null_authorship_unknown(client, report_data):
    resp = client.get("/api/v1/reports/activity?worker_id=rp-w2",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["authorship"] == "unknown"
    assert items[0]["created_by_user_id"] is None


def test_activity_report_date_boundary(client, report_data):
    """Filter by start_date — should exclude wu3 which is 40 days old."""
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    resp = client.get(f"/api/v1/reports/activity?start_date={cutoff}",
                      headers=auth("usr-test-owner", UserRoleEnum.OWNER))
    d = resp.json()
    # wu3 is 40 days old — excluded
    assert all(item["update_id"] != "rp-wu3" for item in d["items"])


def test_activity_report_worker_scope(client, report_data):
    """Workers without scope filter see only their own activity."""
    resp = client.get("/api/v1/reports/activity",
                      headers=auth("rp-w1-u", UserRoleEnum.WORKER))
    d = resp.json()
    assert all(item["worker_id"] == "rp-w1" for item in d["items"])


def test_activity_report_worker_cannot_see_other_worker(client, report_data):
    """Worker cannot filter by another worker's ID."""
    resp = client.get("/api/v1/reports/activity?worker_id=rp-w2",
                      headers=auth("rp-w1-u", UserRoleEnum.WORKER))
    assert resp.status_code == 403


def test_activity_report_unauthenticated(client, report_data):
    resp = client.get("/api/v1/reports/activity")
    assert resp.status_code == 401
