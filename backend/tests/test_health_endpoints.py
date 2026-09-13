from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_liveness_probe():
    """Verify the liveness probe returns 200 without DB."""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" not in data

def test_readiness_probe():
    """Verify the readiness probe checks the database."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "ok"

def test_legacy_health_check():
    """Verify the legacy health check maintains its exact shape."""
    for path in ["/health", "/api/v1/health"]:
        response = client.get(path)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
        assert data["service"] == "Workforce Intelligence API"

def test_security_headers_present():
    """Verify conservative security headers are attached to responses."""
    response = client.get("/api/v1/health/live")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    # HSTS should not be present for http:// testclient requests
    assert "Strict-Transport-Security" not in response.headers

def test_hsts_header_on_https():
    """Verify HSTS is applied to HTTPS requests."""
    # TestClient doesn't easily simulate scheme without base_url, so we simulate the forwarded header
    response = client.get("/api/v1/health/live", headers={"x-forwarded-proto": "https"})
    assert "Strict-Transport-Security" in response.headers
    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
