import pytest
from app.auth.jwt import create_jwt_token
from app.models.user import User, UserRoleEnum, Worker, Supervisor, TeamLeader
from app.models.team import Team
from app.models.project import Project
from app.models.task import Task, TaskStatusEnum, WorkUpdate
from app.core.security import get_password_hash

def get_auth_headers(user_id: str, role: str):
    token = create_jwt_token(user_id, role).access_token
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_data(db_session):
    import uuid
    suffix = uuid.uuid4().hex[:6]
    
    worker_user = User(id=f"usr-w1-{suffix}", name="Worker 1", email=f"w1-{suffix}@test.com", hashed_password="x", role=UserRoleEnum.WORKER, avatar_initials="W1")
    lead_user = User(id=f"usr-l1-{suffix}", name="Lead 1", email=f"l1-{suffix}@test.com", hashed_password="x", role=UserRoleEnum.TEAM_LEADER, avatar_initials="L1")
    sup_user = User(id=f"usr-s1-{suffix}", name="Sup 1", email=f"s1-{suffix}@test.com", hashed_password="x", role=UserRoleEnum.SUPERVISOR, avatar_initials="S1")
    rogue_sup = User(id=f"usr-rogue-{suffix}", name="Rogue", email=f"r-{suffix}@test.com", hashed_password="x", role=UserRoleEnum.SUPERVISOR, avatar_initials="R")
    
    db_session.add_all([worker_user, lead_user, sup_user, rogue_sup])
    db_session.commit()

    sup = Supervisor(id=f"sup-1-{suffix}", user_id=sup_user.id)
    r_sup = Supervisor(id=f"sup-2-{suffix}", user_id=rogue_sup.id)
    team = Team(id=f"team-1-{suffix}", name=f"Team 1 {suffix}", supervisor_id=sup.id)
    lead = TeamLeader(id=f"lead-1-{suffix}", user_id=lead_user.id, team_id=team.id)
    worker = Worker(id=f"wrk-1-{suffix}", user_id=worker_user.id, role="Dev", team_id=team.id)
    
    db_session.add_all([sup, r_sup, team, lead, worker])
    db_session.commit()
    
    from datetime import date
    
    project = Project(id=f"prj-1-{suffix}", name="Proj 1", client="C", start_date=date(2025, 1, 1), deadline=date(2025, 12, 31), supervisor_id=sup.id)
    db_session.add(project)
    
    # Link team to project so TeamLeader has access
    team.projects.append(project)
    db_session.commit()

    task1 = Task(id=f"task-1-{suffix}", project_id=project.id, title="Task 1", assignee_id=worker.id, team_id=team.id, status=TaskStatusEnum.TODO, due_date=date(2025, 6, 1))
    task_unassigned = Task(id=f"task-2-{suffix}", project_id=project.id, title="Task 2", team_id=team.id, status=TaskStatusEnum.TODO, due_date=date(2025, 6, 1))
    
    db_session.add_all([task1, task_unassigned])
    db_session.commit()
    
    return {
        "worker_user": worker_user,
        "lead_user": lead_user,
        "sup_user": sup_user,
        "rogue_sup": rogue_sup,
        "worker": worker,
        "task1": task1,
        "task_unassigned": task_unassigned
    }

def test_worker_can_update_own_task(client, test_data, db_session):
    headers = get_auth_headers(test_data["worker_user"].id, UserRoleEnum.WORKER.value)
    resp = client.post(f"/api/v1/tasks/{test_data['task1'].id}/updates", json={"description": "worker update"}, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["worker_id"] == test_data["worker"].id
    assert data["created_by_user_id"] == test_data["worker_user"].id

def test_team_leader_can_update_team_task(client, test_data):
    headers = get_auth_headers(test_data["lead_user"].id, UserRoleEnum.TEAM_LEADER.value)
    resp = client.post(f"/api/v1/tasks/{test_data['task1'].id}/updates", json={"description": "lead update"}, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["worker_id"] == test_data["worker"].id
    assert data["created_by_user_id"] == test_data["lead_user"].id

def test_supervisor_can_update_team_task(client, test_data):
    headers = get_auth_headers(test_data["sup_user"].id, UserRoleEnum.SUPERVISOR.value)
    resp = client.post(f"/api/v1/tasks/{test_data['task1'].id}/updates", json={"description": "sup update"}, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["worker_id"] == test_data["worker"].id
    assert data["created_by_user_id"] == test_data["sup_user"].id

def test_owner_can_update_task(client, test_data):
    headers = get_auth_headers("usr-test-owner", UserRoleEnum.OWNER.value)
    resp = client.post(f"/api/v1/tasks/{test_data['task1'].id}/updates", json={"description": "owner update"}, headers=headers)
    assert resp.status_code == 201

def test_unauthorized_supervisor_forbidden(client, test_data):
    headers = get_auth_headers(test_data["rogue_sup"].id, UserRoleEnum.SUPERVISOR.value)
    resp = client.post(f"/api/v1/tasks/{test_data['task1'].id}/updates", json={"description": "rogue update"}, headers=headers)
    assert resp.status_code == 403

def test_unassigned_task_bad_request(client, test_data):
    headers = get_auth_headers(test_data["sup_user"].id, UserRoleEnum.SUPERVISOR.value)
    resp = client.post(f"/api/v1/tasks/{test_data['task_unassigned'].id}/updates", json={"description": "unassigned update"}, headers=headers)
    assert resp.status_code == 400
    assert "unassigned" in resp.json()["detail"].lower()
