def test_create_and_get_project(client):
    # 1. Create a project
    new_project = {
        "name": "Test Cloud ERP",
        "client": "Acme Global",
        "description": "Next generation cloud ERP solution",
        "start_date": "2026-09-01",
        "deadline": "2026-12-31",
        "priority": "HIGH",
    }

    create_resp = client.post("/api/v1/projects", json=new_project)
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    assert created_data["name"] == "Test Cloud ERP"
    assert created_data["status"] == "ACTIVE"
    project_id = created_data["id"]

    # 2. Get project by ID
    get_resp = client.get(f"/api/v1/projects/{project_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == project_id

    # 3. List projects
    list_resp = client.get("/api/v1/projects")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1


def test_update_project(client):
    new_project = {
        "name": "Project for Update Test",
        "client": "TechCorp",
        "start_date": "2026-09-01",
        "deadline": "2026-11-30",
        "priority": "MEDIUM",
    }
    create_resp = client.post("/api/v1/projects", json=new_project)
    project_id = create_resp.json()["id"]

    update_resp = client.patch(
        f"/api/v1/projects/{project_id}",
        json={"progress": 45, "health": "AT_RISK"},
    )
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["progress"] == 45
    assert updated_data["health"] == "AT_RISK"
