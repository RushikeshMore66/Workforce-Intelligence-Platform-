from datetime import date

from app.auth.jwt import create_jwt_token
from app.models.project import Project
from app.models.task import Task, TaskStatusEnum
from app.models.user import UserRoleEnum


def get_auth_headers():
    token = create_jwt_token("usr-test-owner", UserRoleEnum.OWNER.value).access_token
    return {"Authorization": f"Bearer {token}"}


def test_create_and_get_project(client, db_session):
    new_project = {
        "name": "Test Cloud ERP",
        "client": "Acme Global",
        "description": "Next generation cloud ERP solution",
        "start_date": "2026-09-01",
        "deadline": "2026-12-31",
        "priority": "HIGH",
    }

    create_resp = client.post(
        "/api/v1/projects",
        json=new_project,
        headers=get_auth_headers(),
    )
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    assert created_data["name"] == "Test Cloud ERP"
    assert created_data["status"] == "PLANNED"
    assert created_data["progress"] == 0

    project_id = created_data["id"]

    get_resp = client.get(
        f"/api/v1/projects/{project_id}",
        headers=get_auth_headers(),
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == project_id

    list_resp = client.get(
        "/api/v1/projects",
        headers=get_auth_headers(),
    )
    assert list_resp.status_code == 200
    assert any(project["id"] == project_id for project in list_resp.json())


def test_update_project_metadata_does_not_allow_manual_progress(client):
    new_project = {
        "name": "Project for Update Test",
        "client": "TechCorp",
        "start_date": "2026-09-01",
        "deadline": "2026-11-30",
        "priority": "MEDIUM",
    }

    create_resp = client.post(
        "/api/v1/projects",
        json=new_project,
        headers=get_auth_headers(),
    )
    project_id = create_resp.json()["id"]

    update_resp = client.patch(
        f"/api/v1/projects/{project_id}",
        json={"progress": 45, "health": "AT_RISK"},
        headers=get_auth_headers(),
    )

    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["progress"] == 0
    assert updated_data["health"] == "AT_RISK"


def test_project_completion_requires_completed_tasks(client, db_session):
    project = Project(
        id="project-completion-test",
        name="Completion Gate",
        client="Acme",
        start_date=date(2026, 9, 1),
        deadline=date(2026, 12, 31),
        priority="HIGH",
    )
    db_session.add(project)

    task = Task(
        id="task-completion-test",
        project_id=project.id,
        title="Finish core implementation",
        status=TaskStatusEnum.PLANNED,
        due_date=date(2026, 10, 1),
    )
    db_session.add(task)
    db_session.commit()

    activate = client.post(
        f"/api/v1/projects/{project.id}/status",
        json={"status": "ACTIVE"},
        headers=get_auth_headers(),
    )
    assert activate.status_code == 200

    blocked_completion = client.post(
        f"/api/v1/projects/{project.id}/status",
        json={"status": "COMPLETED"},
        headers=get_auth_headers(),
    )
    assert blocked_completion.status_code == 403
    assert "not completed" in blocked_completion.json()["detail"].lower()

    task.status = TaskStatusEnum.COMPLETED
    db_session.commit()

    completed = client.post(
        f"/api/v1/projects/{project.id}/status",
        json={"status": "COMPLETED"},
        headers=get_auth_headers(),
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "COMPLETED"


def test_project_hold_requires_reason(client, db_session):
    project = Project(
        id="project-hold-test",
        name="Hold Test",
        client="Acme",
        start_date=date(2026, 9, 1),
        deadline=date(2026, 12, 31),
        priority="MEDIUM",
    )
    db_session.add(project)
    db_session.commit()

    activate = client.post(
        f"/api/v1/projects/{project.id}/status",
        json={"status": "ACTIVE"},
        headers=get_auth_headers(),
    )
    assert activate.status_code == 200

    without_reason = client.post(
        f"/api/v1/projects/{project.id}/status",
        json={"status": "ON_HOLD"},
        headers=get_auth_headers(),
    )
    assert without_reason.status_code == 403

    with_reason = client.post(
        f"/api/v1/projects/{project.id}/status",
        json={"status": "ON_HOLD", "reason": "Waiting for client approval."},
        headers=get_auth_headers(),
    )
    assert with_reason.status_code == 200
    assert with_reason.json()["status"] == "ON_HOLD"
