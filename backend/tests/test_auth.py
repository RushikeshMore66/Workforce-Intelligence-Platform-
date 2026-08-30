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


def test_get_me(client):
    # Test getting current user profile
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "rajesh.mehta@apexsoftware.in", "password": "password123"},
    )
    token = login_resp.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "rajesh.mehta@apexsoftware.in"
    assert data["role"] == "OWNER"
