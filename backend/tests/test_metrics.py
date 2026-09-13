import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.observability.metrics import HTTP_REQUESTS_IN_PROGRESS, REGISTRY

@pytest.fixture
def client_metrics():
    # Ensure metrics are enabled for these tests
    settings.METRICS_ENABLED = True
    with TestClient(app) as c:
        yield c

def test_metrics_endpoint_exists(client_metrics: TestClient):
    """Test 1 — Metrics Endpoint Exists"""
    response = client_metrics.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

def test_request_counter_increases(client_metrics: TestClient):
    """Test 2 — Request Counter Increases"""
    # clear registry before if needed, but we can just check existence
    client_metrics.get("/api/v1/health/live")
    
    response = client_metrics.get("/metrics")
    text = response.text
    
    # Verify the metric contains the correct labels
    # prometheus_client outputs labels like: workforce_http_requests_total{method="GET",route="/api/v1/health/live",status="200"}
    assert 'workforce_http_requests_total{method="GET",route="/api/v1/health/live",status="200"}' in text or \
           'workforce_http_requests_total_total{method="GET",route="/api/v1/health/live",status="200"}' in text

def test_duration_histogram_exists(client_metrics: TestClient):
    """Test 3 — Duration Histogram Exists"""
    client_metrics.get("/api/v1/health/live")
    
    response = client_metrics.get("/metrics")
    assert "workforce_http_request_duration_seconds" in response.text

def test_404_uses_bounded_label(client_metrics: TestClient):
    """Test 4 — 404 Uses Bounded Label"""
    response = client_metrics.get("/nonexistent-random-path-12345")
    assert response.status_code == 404
    
    metrics_response = client_metrics.get("/metrics")
    assert 'route="<unmatched>"' in metrics_response.text
    assert "nonexistent-random-path-12345" not in metrics_response.text

def test_dynamic_ids_are_not_labels(client_metrics: TestClient):
    """Test 5 — Dynamic IDs Are Not Labels"""
    # Assuming there's a route like /api/v1/projects/{project_id}
    # It might return 401 Unauthorized if no auth, but that's fine for testing metrics
    client_metrics.get("/api/v1/projects/123")
    
    metrics_response = client_metrics.get("/metrics")
    assert 'route="/api/v1/projects/{project_id}"' in metrics_response.text
    assert 'route="/api/v1/projects/123"' not in metrics_response.text

def test_status_codes_are_recorded(client_metrics: TestClient):
    """Test 6 — Status Codes Are Recorded"""
    client_metrics.get("/api/v1/health/live")  # 200
    client_metrics.get("/nonexistent-404")     # 404
    
    metrics_response = client_metrics.get("/metrics")
    assert 'status="200"' in metrics_response.text
    assert 'status="404"' in metrics_response.text

def test_in_progress_gauge_returns_to_zero(client_metrics: TestClient):
    """Test 7 — In-Progress Gauge Returns to Zero"""
    # We can check the gauge value directly from the registry
    client_metrics.get("/api/v1/health/live")
    
    # get the value of the gauge
    # method="GET", route="<pending>"
    val = REGISTRY.get_sample_value("workforce_http_requests_in_progress", {"method": "GET", "route": "<pending>"})
    assert val == 0.0

def test_metrics_endpoint_is_excluded(client_metrics: TestClient):
    """Test 8 — Metrics Endpoint Is Excluded"""
    # Just call metrics
    client_metrics.get("/metrics")
    
    metrics_response = client_metrics.get("/metrics")
    assert 'route="/metrics"' not in metrics_response.text

def test_metrics_can_be_disabled(client_metrics: TestClient):
    """Test 9 — Metrics Can Be Disabled"""
    settings.METRICS_ENABLED = False
    response = client_metrics.get("/metrics")
    assert response.status_code == 404
    settings.METRICS_ENABLED = True

def test_no_sensitive_labels(client_metrics: TestClient):
    """Test 10 — No Sensitive Labels"""
    client_metrics.get("/api/v1/health/live", headers={"X-Request-ID": "sensitive-123"})
    metrics_response = client_metrics.get("/metrics")
    
    text = metrics_response.text
    assert "sensitive-123" not in text
    assert "user_id" not in text
    assert "email" not in text
    assert "password" not in text
    assert "DATABASE_URL" not in text
