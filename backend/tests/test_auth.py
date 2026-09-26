"""Auth endpoint tests.

Uses the shared conftest.py owner user (rajesh.mehta@apexsoftware.in / password123).
"""


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "rajesh.mehta@apexsoftware.in", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "rajesh.mehta@apexsoftware.in", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "anything"},
    )
    assert response.status_code == 401


def test_get_me(client):
    """Authenticated /auth/me returns correct user profile including is_active."""
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "rajesh.mehta@apexsoftware.in", "password": "password123"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "rajesh.mehta@apexsoftware.in"
    assert data["role"] == "OWNER"
    assert data["is_active"] is True


def test_get_me_without_token(client):
    """Missing token must return 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_with_invalid_token(client):
    """Malformed token must return 401."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer this.is.not.a.valid.token"},
    )
    assert response.status_code == 401

