import os
import tempfile
import warnings
import pytest
from pydantic import ValidationError
from app.config import Settings

def test_production_rejects_weak_secret():
    """Verify that production validation rejects known unsafe secrets."""
    with pytest.raises(ValidationError, match="known unsafe placeholder"):
        Settings(
            ENVIRONMENT="production",
            DATABASE_URL="postgresql://user:pass@localhost/db",
            SECRET_KEY="super-secret-production-key-change-in-env"
        )

def test_production_rejects_short_secret():
    """Verify that a secret shorter than 32 chars is rejected."""
    with pytest.raises(ValidationError, match="at least 32 characters"):
        Settings(
            ENVIRONMENT="production",
            DATABASE_URL="postgresql://user:pass@localhost/db",
            SECRET_KEY="short"
        )

def test_production_rejects_sqlite():
    """Verify that sqlite databases are rejected in production."""
    with pytest.raises(ValidationError, match="SQLite is not allowed in production"):
        Settings(
            ENVIRONMENT="production",
            DATABASE_URL="sqlite:///./workforce.db",
            SECRET_KEY="a" * 32
        )

def test_production_rejects_long_jwt_expiry():
    """Verify that tokens exceeding 60 minutes are rejected in production."""
    with pytest.raises(ValidationError, match="ACCESS_TOKEN_EXPIRE_MINUTES cannot exceed 60"):
        Settings(
            ENVIRONMENT="production",
            DATABASE_URL="postgresql://user:pass@localhost/db",
            SECRET_KEY="a" * 32,
            ACCESS_TOKEN_EXPIRE_MINUTES=1440
        )

def test_algorithm_whitelist():
    """Verify that only whitelisted algorithms are allowed."""
    with pytest.raises(ValidationError, match="ALGORITHM must be one of"):
        Settings(
            DATABASE_URL="postgresql://user:pass@localhost/db",
            SECRET_KEY="a" * 32,
            ALGORITHM="none"
        )

def test_development_allows_sqlite():
    """Verify that development allows sqlite databases."""
    settings = Settings(
        ENVIRONMENT="development",
        DATABASE_URL="sqlite:///./workforce.db",
        SECRET_KEY="a" * 32
    )
    assert settings.DATABASE_URL == "sqlite:///./workforce.db"

def test_production_warns_cors_wildcard():
    """Verify that wildcard CORS triggers a warning in production."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        Settings(
            ENVIRONMENT="production",
            DATABASE_URL="postgresql://user:pass@localhost/db",
            SECRET_KEY="a" * 32,
            ACCESS_TOKEN_EXPIRE_MINUTES=30,
            BACKEND_CORS_ORIGINS=["*"]
        )
        assert len(w) == 1
        assert "Wildcard CORS ('*') is discouraged in production" in str(w[-1].message)

def test_storage_validation_when_scheduler_enabled():
    """Verify that enabling the scheduler validates the storage path."""
    with tempfile.NamedTemporaryFile() as tmp:
        # Pass a file instead of a directory
        with pytest.raises(ValidationError, match="exists as a file"):
            Settings(
                DATABASE_URL="postgresql://user:pass@localhost/db",
                SECRET_KEY="a" * 32,
                REPORT_SCHEDULER_ENABLED=True,
                REPORT_STORAGE_PATH=tmp.name
            )

def test_boolean_parsing():
    """Verify that boolean environment variables parse correctly from strings."""
    settings = Settings(
        DATABASE_URL="postgresql://user:pass@localhost/db",
        SECRET_KEY="a" * 32,
        REPORT_SCHEDULER_ENABLED="true",
        TRUSTED_HOST_ENABLED="1"
    )
    assert settings.REPORT_SCHEDULER_ENABLED is True
    assert settings.TRUSTED_HOST_ENABLED is True

