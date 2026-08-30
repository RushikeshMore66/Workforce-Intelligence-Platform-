def test_get_dashboard_metrics(client):
    response = client.get("/api/v1/dashboard/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_workers" in data
    assert "active_projects" in data
    assert "tasks_completed" in data


def test_get_attention_items(client):
    response = client.get("/api/v1/dashboard/attention")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_analytics(client):
    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "task_completion" in data
    assert "team_workload" in data
