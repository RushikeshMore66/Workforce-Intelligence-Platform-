from app.auth.jwt import create_jwt_token
from app.models.user import UserRoleEnum

def get_auth_headers():
    token = create_jwt_token("usr-test-owner", UserRoleEnum.OWNER.value).access_token
    return {"Authorization": f"Bearer {token}"}

def test_get_dashboard_metrics(client):
    response = client.get("/api/v1/dashboard/metrics", headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert "total_workers" in data
    assert "active_projects" in data
    assert "tasks_completed" in data


def test_get_attention_items(client):
    response = client.get("/api/v1/dashboard/attention", headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_analytics(client):
    response = client.get("/api/v1/analytics", headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert "task_completion" in data
    assert "team_workload" in data
