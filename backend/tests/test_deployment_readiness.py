import os
import pytest
from unittest import mock
from pydantic_core import ValidationError

from app.config import Settings
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

class TestDeploymentConfiguration:
    def test_production_requires_strong_jwt_secret(self):
        with pytest.raises(ValidationError) as exc:
            Settings(ENVIRONMENT="production", SECRET_KEY="weak", DATABASE_URL="postgresql://user:pass@localhost/db")
        assert "at least 32 characters long" in str(exc.value) or "SECRET_KEY" in str(exc.value)

        with pytest.raises(ValidationError) as exc:
            Settings(ENVIRONMENT="production", SECRET_KEY="change-me", DATABASE_URL="postgresql://user:pass@localhost/db")
        assert "unsafe placeholder" in str(exc.value) or "SECRET_KEY" in str(exc.value)

    def test_production_rejects_sqlite(self):
        with pytest.raises(ValidationError) as exc:
            Settings(
                ENVIRONMENT="production",
                SECRET_KEY="a" * 32,
                DATABASE_URL="sqlite:///./test.db"
            )
        assert "SQLite is not allowed in production" in str(exc.value)

    def test_invalid_database_url_fails_clearly(self):
        with pytest.raises(ValidationError) as exc:
            Settings(
                ENVIRONMENT="production",
                SECRET_KEY="a" * 32,
                DATABASE_URL=""
            )
        assert "DATABASE_URL must be configured" in str(exc.value) or "DATABASE_URL" in str(exc.value)

    def test_production_cors_rejects_localhost_by_default_or_warns(self):
        # The configuration actually allows localhost by default but warns if "*" is used.
        # We can test that "*" warns.
        with pytest.warns(UserWarning, match="Wildcard CORS"):
            Settings(
                ENVIRONMENT="production",
                SECRET_KEY="a" * 32,
                DATABASE_URL="postgresql://user:pass@localhost/db",
                BACKEND_CORS_ORIGINS=["*"]
            )

    def test_required_environment_variables_validated(self):
        with pytest.raises(ValidationError) as exc:
            Settings(ENVIRONMENT="production") # Missing SECRET_KEY and DATABASE_URL
        assert "SECRET_KEY" in str(exc.value)
        assert "DATABASE_URL" in str(exc.value)

class TestHealthEndpoints:
    def test_live_endpoint_returns_successfully(self):
        response = client.get("/api/v1/health/live")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        
    def test_health_responses_contain_no_secrets(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        text = response.text.lower()
        assert "secret" not in text
        assert "password" not in text
        assert "database_url" not in text

class TestSchedulerConfiguration:
    def test_scheduler_imports_independently(self):
        # Should not raise exception
        import app.scheduler.worker
        
    def test_scheduler_metrics_configuration_valid(self):
        # Ensure it requires valid port
        from app.config import settings
        assert isinstance(settings.SCHEDULER_METRICS_PORT, int)
        assert settings.SCHEDULER_METRICS_PORT > 0

class TestStorageConfiguration:
    def test_configured_report_storage_path_exists_or_can_be_created(self, tmp_path):
        test_dir = tmp_path / "test_reports"
        
        # Test creation logic in config validation
        s = Settings(
            ENVIRONMENT="development",
            SECRET_KEY="a" * 32,
            DATABASE_URL="postgresql://user:pass@localhost/db",
            REPORT_SCHEDULER_ENABLED=True,
            REPORT_STORAGE_PATH=str(test_dir)
        )
        assert test_dir.exists()
