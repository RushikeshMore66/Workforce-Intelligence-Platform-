import pytest
from datetime import datetime, timedelta, date
from fastapi.testclient import TestClient
from app.auth.jwt import create_jwt_token
from app.models.user import User, UserRoleEnum, Worker, Supervisor, TeamLeader, WorkerStatusEnum
from app.models.team import Team, team_projects
from app.models.project import Project, ProjectStatusEnum, ProjectPriorityEnum, ProjectHealthEnum
from app.models.task import Task, TaskStatusEnum, WorkUpdate, TaskTransition
from app.core.security import get_password_hash

def get_auth_headers(user_id: str, role: UserRoleEnum):
    token = create_jwt_token(user_id, role.value).access_token
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def org_test_data(db_session):
    # Clear existing data to avoid IntegrityError and isolate counts
    db_session.query(TaskTransition).delete()
    db_session.query(WorkUpdate).delete()
    db_session.query(Task).delete()
    db_session.query(team_projects).delete()
    db_session.query(Project).delete()
    db_session.query(Worker).delete()
    db_session.query(TeamLeader).delete()
    db_session.query(Team).delete()
    db_session.query(Supervisor).delete()
    db_session.query(User).filter(User.id != "usr-test-owner").delete()
    db_session.commit()

    # Create users
    owner = db_session.query(User).filter(User.id == "usr-test-owner").first()
    sup = User(id="usr-sup", name="Sup", email="sup@test.com", hashed_password="hash", role=UserRoleEnum.SUPERVISOR, avatar_initials="SU")
    tl = User(id="usr-tl", name="TL", email="tl@test.com", hashed_password="hash", role=UserRoleEnum.TEAM_LEADER, avatar_initials="TL")
    w1_u = User(id="usr-w1", name="W1", email="w1@test.com", hashed_password="hash", role=UserRoleEnum.WORKER, avatar_initials="W1")
    w2_u = User(id="usr-w2", name="W2", email="w2@test.com", hashed_password="hash", role=UserRoleEnum.WORKER, avatar_initials="W2")
    db_session.add_all([sup, tl, w1_u, w2_u])
    db_session.commit()

    team = Team(id="team-1", name="Team 1")
    db_session.add(team)
    db_session.commit()

    w1 = Worker(id="w-1", user_id="usr-w1", role="Dev", team_id="team-1", status=WorkerStatusEnum.ACTIVE)
    w2 = Worker(id="w-2", user_id="usr-w2", role="Dev", team_id="team-1", status=WorkerStatusEnum.ON_LEAVE)
    w3_no_team = Worker(id="w-3", user_id="usr-sup", role="Dev", team_id=None, status=WorkerStatusEnum.ACTIVE) # weird but ok
    db_session.add_all([w1, w2, w3_no_team])
    db_session.commit()

    p1 = Project(id="p-1", name="P1", client="C1", start_date=date(2026, 1, 1), deadline=date(2026, 12, 31), status=ProjectStatusEnum.ACTIVE, health=ProjectHealthEnum.ON_TRACK)
    p2 = Project(id="p-2", name="P2", client="C1", start_date=date(2026, 1, 1), deadline=date(2026, 12, 31), status=ProjectStatusEnum.PLANNED, health=ProjectHealthEnum.DELAYED)
    db_session.add_all([p1, p2])
    db_session.commit()

    # Tasks
    # t1: COMPLETED, assigned to w1, not overdue (completed)
    t1 = Task(id="t-1", project_id="p-1", title="T1", assignee_id="w-1", status=TaskStatusEnum.COMPLETED, due_date=date.today() - timedelta(days=1))
    # t2: BLOCKED, unassigned, overdue
    t2 = Task(id="t-2", project_id="p-1", title="T2", assignee_id=None, status=TaskStatusEnum.BLOCKED, due_date=date.today() - timedelta(days=5))
    # t3: IN_PROGRESS, assigned to w2, not overdue
    t3 = Task(id="t-3", project_id="p-2", title="T3", assignee_id="w-2", status=TaskStatusEnum.IN_PROGRESS, due_date=date.today() + timedelta(days=10))
    db_session.add_all([t1, t2, t3])
    db_session.commit()

    # Transitions for cycle time
    now = datetime.utcnow()
    # t1: valid cycle time (2 hours)
    tr1 = TaskTransition(id="tr-1", task_id="t-1", from_status=TaskStatusEnum.TODO, to_status=TaskStatusEnum.IN_PROGRESS, timestamp=now - timedelta(hours=4))
    tr2 = TaskTransition(id="tr-2", task_id="t-1", from_status=TaskStatusEnum.IN_PROGRESS, to_status=TaskStatusEnum.COMPLETED, timestamp=now - timedelta(hours=2))
    db_session.add_all([tr1, tr2])
    db_session.commit()

    # WorkUpdates
    # Worker authored by w1 (3 days ago)
    wu1 = WorkUpdate(id="wu-1", task_id="t-1", worker_id="w-1", created_by_user_id="usr-w1", description="U1", timestamp=now - timedelta(days=3))
    # Management authored by sup (10 days ago)
    wu2 = WorkUpdate(id="wu-2", task_id="t-1", worker_id="w-1", created_by_user_id="usr-sup", description="U2", timestamp=now - timedelta(days=10))
    # Legacy unknown authored (null)
    wu3 = WorkUpdate(id="wu-3", task_id="t-2", worker_id="w-2", created_by_user_id=None, description="U3", timestamp=now - timedelta(days=40))
    db_session.add_all([wu1, wu2, wu3])
    db_session.commit()


def test_rbac_organization_analytics(client, org_test_data):
    # Only OWNER can access
    resp = client.get("/api/v1/analytics/organization", headers=get_auth_headers("usr-sup", UserRoleEnum.SUPERVISOR))
    assert resp.status_code == 403

    resp = client.get("/api/v1/analytics/organization", headers=get_auth_headers("usr-w1", UserRoleEnum.WORKER))
    assert resp.status_code == 403

    # Assuming a TEAM_LEADER token would also be 403, we can create one on the fly or just rely on the role
    resp = client.get("/api/v1/analytics/organization", headers=get_auth_headers("usr-tl", UserRoleEnum.TEAM_LEADER))
    assert resp.status_code == 403

    resp = client.get("/api/v1/analytics/organization", headers=get_auth_headers("usr-test-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200

def test_organization_metrics(client, org_test_data):
    resp = client.get("/api/v1/analytics/organization", headers=get_auth_headers("usr-test-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    data = resp.json()

    # Workforce
    wf = data["workforce"]
    assert wf["total_workers"] == 3
    assert wf["active_workers"] == 2
    assert wf["workers_with_tasks"] == 2 # w1, w2
    assert wf["workers_without_tasks"] == 1 # w3
    assert wf["total_teams"] == 1
    assert wf["active_teams"] == 1 # 1 team with workers
    assert wf["total_projects"] == 2
    assert wf["active_projects"] == 1

    # Workload
    wl = data["workload"]
    assert wl["total"] == 3
    assert wl["todo"] == 0
    assert wl["in_progress"] == 1
    assert wl["blocked"] == 1
    assert wl["completed"] == 1
    assert wl["overdue"] == 1 # t2
    assert wl["unassigned"] == 1 # t2

    # Activity
    act = data["activity"]
    assert act["total_updates"] == 3
    assert act["updates_last_7_days"] == 1 # wu1
    assert act["updates_last_30_days"] == 2 # wu1, wu2
    assert act["worker_authored_updates"] == 1 # wu1
    assert act["management_authored_updates"] == 1 # wu2 (wu3 is None)

    # Delivery
    deliv = data["delivery"]
    assert deliv["completed_tasks"] == 1
    assert deliv["completion_rate"] == 1/3
    assert deliv["average_cycle_time_hours"] == 2.0
    assert deliv["tasks_with_valid_transition_history"] == 1
    assert deliv["tasks_missing_transition_history"] == 0

    # Attention
    attn = data["attention"]
    assert attn["overdue_tasks"] == 1
    assert attn["blocked_tasks"] == 1
    assert attn["unassigned_tasks"] == 1
    assert attn["at_risk_projects"] == 1 # p2 is delayed
    assert attn["workers_with_no_recent_activity"] == 2 # w2, w3 have no updates in last 7 days


def test_zero_organization_metrics(client, db_session):
    # Clear all data
    db_session.query(TaskTransition).delete()
    db_session.query(WorkUpdate).delete()
    db_session.query(Task).delete()
    db_session.query(team_projects).delete()
    db_session.query(Project).delete()
    db_session.query(Worker).delete()
    db_session.query(TeamLeader).delete()
    db_session.query(Team).delete()
    db_session.commit()

    resp = client.get("/api/v1/analytics/organization", headers=get_auth_headers("usr-test-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    data = resp.json()

    assert data["workforce"]["total_workers"] == 0
    assert data["workload"]["total"] == 0
    assert data["activity"]["total_updates"] == 0
    assert data["delivery"]["completed_tasks"] == 0
    assert data["delivery"]["completion_rate"] == 0.0
    assert data["delivery"]["average_cycle_time_hours"] is None
    assert data["delivery"]["tasks_with_valid_transition_history"] == 0
    assert data["delivery"]["tasks_missing_transition_history"] == 0
    assert data["attention"]["overdue_tasks"] == 0
    assert data["attention"]["workers_with_no_recent_activity"] == 0
