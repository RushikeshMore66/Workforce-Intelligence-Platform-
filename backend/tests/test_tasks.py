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
from app.models.task import TaskTransition

def test_task_status_transition_todo_to_in_progress(client, test_data, db_session):
    headers = get_auth_headers(test_data["worker_user"].id, UserRoleEnum.WORKER.value)
    
    # 1. TODO -> IN_PROGRESS
    resp = client.patch(
        f"/api/v1/tasks/{test_data['task1'].id}",
        json={"status": "IN_PROGRESS"},
        headers=headers
    )
    assert resp.status_code == 200
    
    # Verify exactly one transition
    transitions = db_session.query(TaskTransition).filter(TaskTransition.task_id == test_data['task1'].id).all()
    assert len(transitions) == 1
    t = transitions[0]
    assert t.from_status == TaskStatusEnum.TODO
    assert t.to_status == TaskStatusEnum.IN_PROGRESS
    assert t.changed_by_user_id == test_data["worker_user"].id


def test_task_status_unchanged_creates_no_transition(client, test_data, db_session):
    headers = get_auth_headers(test_data["worker_user"].id, UserRoleEnum.WORKER.value)
    
    # Ensure starting status is TODO
    task = test_data['task1']
    task.status = TaskStatusEnum.TODO
    db_session.commit()
    
    resp = client.patch(
        f"/api/v1/tasks/{task.id}",
        json={"status": "TODO", "title": "Updated Title"},
        headers=headers
    )
    assert resp.status_code == 200
    
    # Verify no transitions created
    transitions = db_session.query(TaskTransition).filter(TaskTransition.task_id == task.id).all()
    assert len(transitions) == 0


def test_sequential_status_transitions(client, test_data, db_session):
    headers = get_auth_headers(test_data["worker_user"].id, UserRoleEnum.WORKER.value)
    task_id = test_data['task1'].id
    
    # TODO -> IN_PROGRESS
    client.patch(f"/api/v1/tasks/{task_id}", json={"status": "IN_PROGRESS"}, headers=headers)
    # IN_PROGRESS -> BLOCKED
    client.patch(f"/api/v1/tasks/{task_id}", json={"status": "BLOCKED"}, headers=headers)
    # BLOCKED -> IN_PROGRESS
    client.patch(f"/api/v1/tasks/{task_id}", json={"status": "IN_PROGRESS"}, headers=headers)
    # IN_PROGRESS -> COMPLETED
    client.patch(f"/api/v1/tasks/{task_id}", json={"status": "COMPLETED"}, headers=headers)
    
    transitions = db_session.query(TaskTransition).filter(TaskTransition.task_id == task_id).order_by(TaskTransition.timestamp.asc()).all()
    assert len(transitions) == 4
    
    assert transitions[0].from_status == TaskStatusEnum.TODO
    assert transitions[0].to_status == TaskStatusEnum.IN_PROGRESS
    
    assert transitions[1].from_status == TaskStatusEnum.IN_PROGRESS
    assert transitions[1].to_status == TaskStatusEnum.BLOCKED
    
    assert transitions[2].from_status == TaskStatusEnum.BLOCKED
    assert transitions[2].to_status == TaskStatusEnum.IN_PROGRESS
    
    assert transitions[3].from_status == TaskStatusEnum.IN_PROGRESS
    assert transitions[3].to_status == TaskStatusEnum.COMPLETED


def test_unauthorized_user_cannot_create_transition(client, test_data, db_session):
    headers = get_auth_headers(test_data["rogue_sup"].id, UserRoleEnum.SUPERVISOR.value)
    task_id = test_data['task1'].id
    
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "IN_PROGRESS"}, headers=headers)
    assert resp.status_code == 403
    
    # Verify no transition
    transitions = db_session.query(TaskTransition).filter(TaskTransition.task_id == task_id).all()
    assert len(transitions) == 0


def test_client_cannot_spoof_changed_by_user_id(client, test_data, db_session):
    headers = get_auth_headers(test_data["worker_user"].id, UserRoleEnum.WORKER.value)
    task_id = test_data['task1'].id
    
    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "IN_PROGRESS", "changed_by_user_id": "some-other-id"}, headers=headers)
    assert resp.status_code == 200
    
    # Verify transition has the authenticated user, not the spoofed one
    transitions = db_session.query(TaskTransition).filter(TaskTransition.task_id == task_id).all()
    assert len(transitions) == 1
    assert transitions[0].changed_by_user_id == test_data["worker_user"].id


def test_task_deletion_cascades_transitions(client, test_data, db_session):
    headers = get_auth_headers(test_data["worker_user"].id, UserRoleEnum.WORKER.value)
    task_id = test_data['task1'].id
    
    # Create transition
    client.patch(f"/api/v1/tasks/{task_id}", json={"status": "IN_PROGRESS"}, headers=headers)
    
    transitions = db_session.query(TaskTransition).filter(TaskTransition.task_id == task_id).all()
    assert len(transitions) == 1
    
    # Delete task directly from db to test cascade
    task = db_session.query(Task).filter(Task.id == task_id).first()
    db_session.delete(task)
    db_session.commit()
    
    # Verify transitions are deleted
    transitions_after = db_session.query(TaskTransition).filter(TaskTransition.task_id == task_id).all()
    assert len(transitions_after) == 0
