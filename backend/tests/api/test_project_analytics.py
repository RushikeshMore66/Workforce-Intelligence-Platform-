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
def test_data(db_session):
    # Clear existing data to avoid IntegrityError
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

    # Create test users
    owner = User(id="usr-owner", name="Owner", email="owner@test.com", hashed_password="hash", role=UserRoleEnum.OWNER, avatar_initials="OW")
    sup_user = User(id="usr-sup", name="Sup", email="sup@test.com", hashed_password="hash", role=UserRoleEnum.SUPERVISOR, avatar_initials="SU")
    sup2_user = User(id="usr-sup2", name="Sup2", email="sup2@test.com", hashed_password="hash", role=UserRoleEnum.SUPERVISOR, avatar_initials="S2")
    tl_user = User(id="usr-tl", name="TL", email="tl@test.com", hashed_password="hash", role=UserRoleEnum.TEAM_LEADER, avatar_initials="TL")
    tl2_user = User(id="usr-tl2", name="TL2", email="tl2@test.com", hashed_password="hash", role=UserRoleEnum.TEAM_LEADER, avatar_initials="T2")
    w1_user = User(id="usr-w1", name="W1", email="w1@test.com", hashed_password="hash", role=UserRoleEnum.WORKER, avatar_initials="W1")
    w2_user = User(id="usr-w2", name="W2", email="w2@test.com", hashed_password="hash", role=UserRoleEnum.WORKER, avatar_initials="W2")
    w3_user = User(id="usr-w3", name="W3", email="w3@test.com", hashed_password="hash", role=UserRoleEnum.WORKER, avatar_initials="W3")
    
    db_session.add_all([owner, sup_user, sup2_user, tl_user, tl2_user, w1_user, w2_user, w3_user])
    db_session.commit()

    # Profiles
    sup = Supervisor(id="sup-1", user_id="usr-sup")
    sup2 = Supervisor(id="sup-2", user_id="usr-sup2")
    db_session.add_all([sup, sup2])
    db_session.commit()

    team1 = Team(id="team-1", name="Team 1", supervisor_id="sup-1")
    team2 = Team(id="team-2", name="Team 2", supervisor_id="sup-2")
    db_session.add_all([team1, team2])
    db_session.commit()

    tl = TeamLeader(id="tl-1", user_id="usr-tl", team_id="team-1")
    tl2 = TeamLeader(id="tl-2", user_id="usr-tl2", team_id="team-2")
    db_session.add_all([tl, tl2])
    db_session.commit()

    w1 = Worker(id="w-1", user_id="usr-w1", role="Developer", team_id="team-1", status=WorkerStatusEnum.ACTIVE)
    w2 = Worker(id="w-2", user_id="usr-w2", role="Tester", team_id="team-1", status=WorkerStatusEnum.ON_LEAVE)
    w3 = Worker(id="w-3", user_id="usr-w3", role="Outsider", team_id="team-2", status=WorkerStatusEnum.ACTIVE)
    db_session.add_all([w1, w2, w3])
    db_session.commit()

    # Project 1: main testing project
    p1 = Project(id="proj-1", name="Proj 1", client="C1", start_date=date(2026, 1, 1), deadline=date(2026, 12, 31), supervisor_id="sup-1")
    # Project 2: for zero tasks test
    p2 = Project(id="proj-2", name="Proj 2", client="C1", start_date=date(2026, 1, 1), deadline=date(2026, 12, 31), supervisor_id="sup-1")
    # Project 3: for zero workers test
    p3 = Project(id="proj-3", name="Proj 3", client="C1", start_date=date(2026, 1, 1), deadline=date(2026, 12, 31), supervisor_id="sup-1")
    db_session.add_all([p1, p2, p3])
    db_session.commit()

    # Link team1 to p1, p2
    stmt = team_projects.insert().values([(team1.id, p1.id), (team1.id, p2.id)])
    db_session.execute(stmt)
    db_session.commit()

    # Tasks for Project 1
    # t1: COMPLETED (assigned to w1)
    t1 = Task(id="task-1", project_id="proj-1", title="T1", assignee_id="w-1", status=TaskStatusEnum.COMPLETED, due_date=date.today() - timedelta(days=1))
    # t2: IN_PROGRESS (assigned to w3 - outside team!) overdue
    t2 = Task(id="task-2", project_id="proj-1", title="T2", assignee_id="w-3", status=TaskStatusEnum.IN_PROGRESS, due_date=date.today() - timedelta(days=2))
    # t3: TODO (assigned to w2) null due_date essentially (we will just set it to future)
    t3 = Task(id="task-3", project_id="proj-1", title="T3", assignee_id="w-2", status=TaskStatusEnum.TODO, due_date=date.today() + timedelta(days=10))
    # t4: BLOCKED (unassigned) overdue
    t4 = Task(id="task-4", project_id="proj-1", title="T4", assignee_id=None, status=TaskStatusEnum.BLOCKED, due_date=date.today() - timedelta(days=5))
    # t5: TODO (assigned to w1) not overdue
    t5 = Task(id="task-5", project_id="proj-1", title="T5", assignee_id="w-1", status=TaskStatusEnum.TODO, due_date=date.today() + timedelta(days=5))
    db_session.add_all([t1, t2, t3, t4, t5])
    db_session.commit()

    # Task transitions for cycle time
    now = datetime.utcnow()
    # task-1 cycle time: 2 days (48 hours)
    tr1 = TaskTransition(id="tr-1", task_id="task-1", from_status=TaskStatusEnum.TODO, to_status=TaskStatusEnum.IN_PROGRESS, timestamp=now - timedelta(days=5))
    tr2 = TaskTransition(id="tr-2", task_id="task-1", from_status=TaskStatusEnum.IN_PROGRESS, to_status=TaskStatusEnum.COMPLETED, timestamp=now - timedelta(days=3))
    # task-2 cycle time: incomplete (only started)
    tr3 = TaskTransition(id="tr-3", task_id="task-2", from_status=TaskStatusEnum.TODO, to_status=TaskStatusEnum.IN_PROGRESS, timestamp=now - timedelta(days=4))
    # multiple transitions testing FIRST todo->in_progress
    tr4 = TaskTransition(id="tr-4", task_id="task-2", from_status=TaskStatusEnum.IN_PROGRESS, to_status=TaskStatusEnum.BLOCKED, timestamp=now - timedelta(days=3))
    tr5 = TaskTransition(id="tr-5", task_id="task-2", from_status=TaskStatusEnum.BLOCKED, to_status=TaskStatusEnum.IN_PROGRESS, timestamp=now - timedelta(days=2))
    db_session.add_all([tr1, tr2, tr3, tr4, tr5])
    db_session.commit()

    # WorkUpdates
    # Worker authored (w-1) last 7 days
    wu1 = WorkUpdate(id="wu-1", task_id="task-1", worker_id="w-1", created_by_user_id="usr-w1", description="U1", timestamp=now - timedelta(days=2))
    # Management authored (sup) last 30 days
    wu2 = WorkUpdate(id="wu-2", task_id="task-1", worker_id="w-1", created_by_user_id="usr-sup", description="U2", timestamp=now - timedelta(days=15))
    # Worker authored (w-3) beyond 30 days
    wu3 = WorkUpdate(id="wu-3", task_id="task-2", worker_id="w-3", created_by_user_id="usr-w3", description="U3", timestamp=now - timedelta(days=40))
    db_session.add_all([wu1, wu2, wu3])
    db_session.commit()

    # Tasks for Project 3 (0 workers)
    t_p3 = Task(id="task-p3", project_id="proj-3", title="T P3", assignee_id=None, status=TaskStatusEnum.TODO, due_date=date.today() + timedelta(days=10))
    db_session.add(t_p3)
    db_session.commit()

    return {
        "p1": p1.id,
        "p2": p2.id,
        "p3": p3.id,
        "owner": owner,
        "sup": sup_user,
        "sup2": sup2_user,
        "tl": tl_user,
        "tl2": tl2_user,
        "w1": w1_user,
        "w3": w3_user,
    }

# 1. OWNER can access any project
def test_owner_can_access_any_project(client, test_data):
    resp = client.get(f"/api/v1/projects/{test_data['p1']}/analytics", headers=get_auth_headers("usr-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200

# 2. SUPERVISOR can access authorized project
def test_supervisor_authorized(client, test_data):
    resp = client.get(f"/api/v1/projects/{test_data['p1']}/analytics", headers=get_auth_headers("usr-sup", UserRoleEnum.SUPERVISOR))
    assert resp.status_code == 200

# 3. SUPERVISOR cannot access unauthorized project
def test_supervisor_unauthorized(client, test_data):
    # sup2 does not own p1
    resp = client.get(f"/api/v1/projects/{test_data['p1']}/analytics", headers=get_auth_headers("usr-sup2", UserRoleEnum.SUPERVISOR))
    assert resp.status_code == 403

# 4. TEAM_LEADER can access authorized project
def test_team_leader_authorized(client, test_data):
    resp = client.get(f"/api/v1/projects/{test_data['p1']}/analytics", headers=get_auth_headers("usr-tl", UserRoleEnum.TEAM_LEADER))
    assert resp.status_code == 200

# 5. TEAM_LEADER cannot access unauthorized project
def test_team_leader_unauthorized(client, test_data):
    resp = client.get(f"/api/v1/projects/{test_data['p1']}/analytics", headers=get_auth_headers("usr-tl2", UserRoleEnum.TEAM_LEADER))
    assert resp.status_code == 403

# 6. WORKER can access authorized project
def test_worker_authorized(client, test_data):
    resp = client.get(f"/api/v1/projects/{test_data['p1']}/analytics", headers=get_auth_headers("usr-w1", UserRoleEnum.WORKER))
    assert resp.status_code == 200

# 7. WORKER cannot access unauthorized project
def test_worker_unauthorized(client, test_data):
    resp = client.get(f"/api/v1/projects/{test_data['p1']}/analytics", headers=get_auth_headers("usr-w3", UserRoleEnum.WORKER))
    assert resp.status_code == 403

def test_project_analytics_metrics(client, test_data):
    resp = client.get(f"/api/v1/projects/{test_data['p1']}/analytics", headers=get_auth_headers("usr-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    data = resp.json()

    # Workforce
    # 8. Correct official workforce count (Team 1 has w1, w2)
    assert data["workforce"]["total_workers"] == 2
    # 9. Correct active worker count (w1 is active, w2 is on leave)
    assert data["workforce"]["active_workers"] == 1
    # 10. Correct workers_with_tasks count (w1, w2, w3 assigned to p1) -> 3
    assert data["workforce"]["workers_with_tasks"] == 3

    # Workload
    # 11. Correct total workload (5 tasks)
    assert data["workload"]["total"] == 5
    # 12. Correct TODO count (2 tasks)
    assert data["workload"]["todo"] == 2
    # 13. Correct IN_PROGRESS count (1 task)
    assert data["workload"]["in_progress"] == 1
    # 14. Correct BLOCKED count (1 task)
    assert data["workload"]["blocked"] == 1
    # 15. Correct COMPLETED count (1 task)
    assert data["workload"]["completed"] == 1
    # 16, 17. Correct overdue count (t2, t4 are overdue. t1 is completed. t3, t5 future) -> 2
    assert data["workload"]["overdue"] == 2

    # Activity
    # 18. Correct total activity (3 updates)
    assert data["activity"]["total_updates"] == 3
    # 19. Correct 7-day activity (wu1)
    assert data["activity"]["updates_last_7_days"] == 1
    # 20. Correct 30-day activity (wu1, wu2)
    assert data["activity"]["updates_last_30_days"] == 2
    # 21. Correct worker-authored (wu1, wu3)
    assert data["activity"]["worker_authored_updates"] == 2
    # 22. Correct management-authored (wu2)
    assert data["activity"]["management_authored_updates"] == 1
    # 23. Correct last_update_at
    assert data["activity"]["last_update_at"] is not None

    # Delivery
    # 24. Correct completed task count
    assert data["delivery"]["completed_tasks"] == 1
    # 25. Correct completion rate
    assert data["delivery"]["completion_rate"] == 0.2
    # 27, 28, 29, 30, 31. Correct cycle time (48 hours = 172800 seconds)
    assert data["delivery"]["average_cycle_time"] == 172800.0


def test_zero_tasks(client, test_data):
    # 32, 26. Zero tasks
    resp = client.get(f"/api/v1/projects/{test_data['p2']}/analytics", headers=get_auth_headers("usr-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    data = resp.json()
    assert data["workload"]["total"] == 0
    assert data["delivery"]["completion_rate"] == 0.0
    assert data["delivery"]["average_cycle_time"] is None


def test_zero_workers(client, test_data):
    # 33. Zero official workers, but has tasks
    resp = client.get(f"/api/v1/projects/{test_data['p3']}/analytics", headers=get_auth_headers("usr-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    data = resp.json()
    assert data["workforce"]["total_workers"] == 0
    assert data["workload"]["total"] == 1
    assert data["workforce"]["workers_with_tasks"] == 0


def test_zero_tasks_with_workers(client, test_data):
    # 34. Project with official workers but zero tasks works.
    resp = client.get(f"/api/v1/projects/{test_data['p2']}/analytics", headers=get_auth_headers("usr-owner", UserRoleEnum.OWNER))
    assert resp.status_code == 200
    data = resp.json()
    assert data["workforce"]["total_workers"] == 2
    assert data["workload"]["total"] == 0
