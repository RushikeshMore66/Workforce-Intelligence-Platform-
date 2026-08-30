def test_list_workers(client):
    response = client.get("/api/v1/workers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_supervisors(client):
    response = client.get("/api/v1/supervisors")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_teams(client):
    response = client.get("/api/v1/teams")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
