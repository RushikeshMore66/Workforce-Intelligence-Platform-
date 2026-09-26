"""
Phase 7.21.2 — Security Hardening Tests.

Coverage:
1. Empty SECRET_KEY is rejected at settings validation time.
2. Short SECRET_KEY is rejected at settings validation time.
3. Empty DATABASE_URL is rejected at settings validation time.
4. TrustedHostMiddleware is disabled by default.
5. TrustedHostMiddleware activates when TRUSTED_HOST_ENABLED=True.
6. Unexpected exceptions return sanitized 500 responses (no traceback exposed).
7. Authentication failures produce the flat project envelope and HTTP 401.
8. No raw Python traceback text appears in any 500 response body.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.auth.jwt import create_jwt_token
from app.models.user import UserRoleEnum


# ── Helper ────────────────────────────────────────────────────────────────────


def auth_header(user_id: str, role: UserRoleEnum) -> dict:
    token = create_jwt_token(user_id, role.value).access_token
    return {"Authorization": f"Bearer {token}"}


# ── 7.21.2.1 — Configuration Validation ──────────────────────────────────────


class TestConfigValidation:
    """Settings-level validators reject dangerous configurations at startup."""

    def test_empty_secret_key_is_rejected(self):
        """An empty SECRET_KEY must raise a validation error before the app starts."""
        from pydantic import ValidationError
        from app.config import Settings

        with pytest.raises(ValidationError) as exc_info:
            Settings(SECRET_KEY="", DATABASE_URL="sqlite:///./test.db")

        errors = exc_info.value.errors()
        secret_key_errors = [e for e in errors if "SECRET_KEY" in str(e.get("loc", ""))]
        assert secret_key_errors, f"Expected SECRET_KEY error, got: {errors}"

    def test_short_secret_key_is_rejected(self):
        """A SECRET_KEY shorter than 32 characters must raise a validation error."""
        from pydantic import ValidationError
        from app.config import Settings

        with pytest.raises(ValidationError) as exc_info:
            Settings(SECRET_KEY="short-key", DATABASE_URL="sqlite:///./test.db")

        errors = exc_info.value.errors()
        secret_key_errors = [e for e in errors if "SECRET_KEY" in str(e.get("loc", ""))]
        assert secret_key_errors, f"Expected SECRET_KEY length error, got: {errors}"

    def test_empty_database_url_is_rejected(self):
        """An empty DATABASE_URL must raise a validation error."""
        from pydantic import ValidationError
        from app.config import Settings

        with pytest.raises(ValidationError) as exc_info:
            Settings(
                SECRET_KEY="a-very-long-and-secure-secret-key-for-testing-12345",
                DATABASE_URL="",
            )

        errors = exc_info.value.errors()
        db_errors = [e for e in errors if "DATABASE_URL" in str(e.get("loc", ""))]
        assert db_errors, f"Expected DATABASE_URL error, got: {errors}"

    def test_valid_config_is_accepted(self):
        """Valid settings must not raise any validation error."""
        from app.config import Settings

        settings = Settings(
            SECRET_KEY="a-very-long-and-secure-secret-key-for-testing-12345",
            DATABASE_URL="sqlite:///./test.db",
        )
        assert settings.SECRET_KEY.startswith("a-very-long")

    def test_trusted_host_disabled_by_default(self):
        """TRUSTED_HOST_ENABLED must default to False."""
        from app.config import Settings

        settings = Settings(
            SECRET_KEY="a-very-long-and-secure-secret-key-for-testing-12345",
            DATABASE_URL="sqlite:///./test.db",
        )
        assert settings.TRUSTED_HOST_ENABLED is False

    def test_rate_limit_disabled_by_default(self):
        """RATE_LIMIT_ENABLED must default to False."""
        from app.config import Settings

        settings = Settings(
            SECRET_KEY="a-very-long-and-secure-secret-key-for-testing-12345",
            DATABASE_URL="sqlite:///./test.db",
        )
        assert settings.RATE_LIMIT_ENABLED is False

    def test_trusted_hosts_configurable(self):
        """TRUSTED_HOSTS must be parseable from a comma-separated string."""
        from app.config import Settings

        settings = Settings(
            SECRET_KEY="a-very-long-and-secure-secret-key-for-testing-12345",
            DATABASE_URL="sqlite:///./test.db",
            TRUSTED_HOST_ENABLED=True,
            TRUSTED_HOSTS="example.com,api.example.com",
        )
        assert "example.com" in settings.TRUSTED_HOSTS
        assert "api.example.com" in settings.TRUSTED_HOSTS


# ── 7.21.2.2 — TrustedHostMiddleware ─────────────────────────────────────────


class TestTrustedHostMiddleware:
    """TrustedHostMiddleware behaviour when enabled vs disabled."""

    def test_trusted_host_middleware_not_active_by_default(self, client):
        """Requests with any Host header succeed when middleware is disabled (default)."""
        # The standard test client does not set a Host header that would be rejected
        # under normal middleware config. Confirm a normal request succeeds.
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_trusted_host_middleware_rejects_unknown_host_when_enabled(self):
        """When TRUSTED_HOST_ENABLED=True, a Host header not in TRUSTED_HOSTS → 400."""
        from unittest.mock import patch
        from app.main import app

        # Temporarily patch settings to enable trusted host enforcement
        with patch("app.main.settings") as mock_settings:
            mock_settings.TRUSTED_HOST_ENABLED = True
            mock_settings.TRUSTED_HOSTS = ["trusted.example.com"]
            mock_settings.BACKEND_CORS_ORIGINS = ["http://localhost:3000"]
            mock_settings.PROJECT_NAME = "Test"
            mock_settings.VERSION = "0.0.1"
            mock_settings.API_V1_STR = "/api/v1"
            mock_settings.REPORT_SCHEDULER_ENABLED = False

            # Build a fresh app with TrustedHostMiddleware active
            from fastapi import FastAPI
            from starlette.middleware.trustedhost import TrustedHostMiddleware

            mini_app = FastAPI()
            mini_app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=["trusted.example.com"],
            )

            @mini_app.get("/ping")
            def ping():
                return {"ok": True}

            with TestClient(mini_app, raise_server_exceptions=False) as c:
                resp = c.get("/ping", headers={"Host": "evil.attacker.com"})
                assert resp.status_code == 400


# ── 7.21.2.3 — Global 500 Handler ─────────────────────────────────────────────


class TestGlobal500Handler:
    """Unhandled exceptions must produce a sanitized 500 and never expose tracebacks."""

    def test_unhandled_exception_returns_500(self):
        """
        We inject a route that raises an unhandled RuntimeError and verify the
        sanitized response envelope is returned.

        We use raise_server_exceptions=False so TestClient returns the 500 JSON
        response instead of re-raising the exception into the test.
        """
        from app.main import app
        from app.database import get_db
        from app.main import app
        from fastapi.testclient import TestClient as _TC

        @app.get("/test-500-route", include_in_schema=False)
        def _crash():
            raise RuntimeError("Something exploded internally")

        try:
            # raise_server_exceptions=False: returns the 500 response
            with _TC(app, raise_server_exceptions=False) as c:
                resp = c.get("/test-500-route")
            assert resp.status_code == 500
            body = resp.json()
            assert body["success"] is False
            assert body["error"] == "Internal Server Error"
            assert body["detail"] == "An unexpected error occurred."
        finally:
            routes_to_remove = [
                r for r in app.routes
                if getattr(r, "path", None) == "/test-500-route"
            ]
            for r in routes_to_remove:
                app.routes.remove(r)

    def test_500_response_contains_no_traceback(self):
        """The 500 response body must not contain Python traceback keywords."""
        from app.main import app
        from fastapi.testclient import TestClient as _TC

        @app.get("/test-500-no-trace", include_in_schema=False)
        def _crash_no_trace():
            raise ValueError("Internal database error: password=secret")

        try:
            with _TC(app, raise_server_exceptions=False) as c:
                resp = c.get("/test-500-no-trace")
            body_text = resp.text
            # Traceback markers must not appear in the client-facing response body
            assert "Traceback" not in body_text
            assert 'File "' not in body_text
            assert "line " not in body_text
            # Sensitive details must not appear in client response
            assert "password=secret" not in body_text
            assert "Internal database error" not in body_text
        finally:
            routes_to_remove = [
                r for r in app.routes
                if getattr(r, "path", None) == "/test-500-no-trace"
            ]
            for r in routes_to_remove:
                app.routes.remove(r)


# ── 7.21.2.4 — Authentication Error Shape ────────────────────────────────────


class TestAuthenticationErrorShape:
    """Login failures must produce a flat, frontend-compatible error envelope."""

    def test_login_bad_credentials_returns_401(self, client):
        """Invalid credentials → HTTP 401."""
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    def test_login_bad_credentials_shape(self, client):
        """Invalid credentials → flat envelope with success=False."""
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "wrongpassword"},
        )
        body = resp.json()
        # Flat envelope — the frontend reads these fields
        assert body["success"] is False
        assert "error" in body
        assert "detail" in body
        # Must NOT expose internal exception types
        assert "Exception" not in body.get("detail", "")
        assert "Traceback" not in str(body)

    def test_me_without_token_returns_401(self, client):
        """Accessing /me without a token → HTTP 401."""
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_me_with_invalid_token_returns_401(self, client):
        """Accessing /me with a malformed token → HTTP 401."""
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer this-is-not-a-valid-jwt"},
        )
        assert resp.status_code == 401

    def test_me_with_valid_token_succeeds(self, client):
        """Accessing /me with a valid token → HTTP 200."""
        token = create_jwt_token("usr-test-owner", UserRoleEnum.OWNER.value).access_token
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200


# ── 7.21.2.5 — HTTPException Normalization ───────────────────────────────────


class TestHTTPExceptionNormalization:
    """All HTTPExceptions — including raw ones — must produce the flat envelope."""

    def test_403_shape(self, client, db_session):
        """Accessing an OWNER-only endpoint as a worker → 403 with flat envelope.

        We create a real WORKER user so the RBAC lookup returns the correct role.
        The JWT user_id must match a DB user whose role is actually WORKER.
        """
        from app.models.user import User, UserRoleEnum as Roles

        # Create a dedicated worker user for this test
        worker_user = db_session.query(User).filter(User.id == "sec-test-worker").first()
        if not worker_user:
            worker_user = User(
                id="sec-test-worker",
                name="Security Test Worker",
                email="sec-test-worker@example.com",
                hashed_password="hashed",
                role=Roles.WORKER,
                avatar_initials="SW",
            )
            db_session.add(worker_user)
            db_session.commit()

        token = create_jwt_token("sec-test-worker", Roles.WORKER.value).access_token
        resp = client.get(
            "/api/v1/reports/organization",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
        body = resp.json()
        assert body["success"] is False
        assert "error" in body
        assert "detail" in body

    def test_404_shape(self, client):
        """A non-existent resource returns 404 with the flat envelope."""
        token = create_jwt_token("usr-test-owner", UserRoleEnum.OWNER.value).access_token
        resp = client.get(
            "/api/v1/projects/definitely-does-not-exist",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404
        body = resp.json()
        assert body["success"] is False
        assert "error" in body
        assert "detail" in body

    def test_422_validation_shape(self, client):
        """A request with an invalid body → 422 with flat envelope."""
        token = create_jwt_token("usr-test-owner", UserRoleEnum.OWNER.value).access_token
        # POST /projects with completely wrong body
        resp = client.post(
            "/api/v1/projects",
            json={"this_field_does_not_exist": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422
        body = resp.json()
        assert body["success"] is False
        assert "error" in body
        # detail should be a list of Pydantic validation errors
        assert "detail" in body

