from app.auth.jwt import create_jwt_token
from app.models.user import UserRoleEnum

def get_auth_headers():
    token = create_jwt_token("usr-test-owner", UserRoleEnum.OWNER.value).access_token
    return {"Authorization": f"Bearer {token}"}

def test_list_workers(client):
    response = client.get("/api/v1/workers", headers=get_auth_headers())
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_supervisors(client):
    response = client.get("/api/v1/supervisors", headers=get_auth_headers())
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_teams(client):
    response = client.get("/api/v1/teams", headers=get_auth_headers())
    assert response.status_code == 200
    assert isinstance(response.json(), list)
