import uuid

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.main import app
from app.observability.request_context import get_request_id

# We add test-only routes to verify context propagation
test_router = APIRouter()


@test_router.get("/api/v1/_test/request_id")
def get_current_request_id():
    return {"request_id": get_request_id()}


@test_router.get("/api/v1/_test/exception")
def raise_exception():
    raise RuntimeError("Test exception")


app.include_router(test_router)


# Use the client fixture from conftest.py implicitly (or we can just instantiate TestClient here)
@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


def test_existing_request_id_is_preserved(client: TestClient):
    """Test 1 - Existing Request ID Is Preserved"""
    response = client.get(
        "/api/v1/health/live", headers={"X-Request-ID": "test-request-123"}
    )
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-123"


def test_missing_request_id_is_generated(client: TestClient):
    """Test 2 - Missing Request ID Is Generated"""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    req_id = response.headers.get("X-Request-ID")
    assert req_id is not None
    # Verify it is a valid UUID
    uuid_obj = uuid.UUID(req_id)
    assert str(uuid_obj) == req_id


def test_header_is_case_insensitive(client: TestClient):
    """Test 3 - Header Is Case-Insensitive"""
    response = client.get(
        "/api/v1/health/live", headers={"x-request-id": "test-request-lower"}
    )
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-lower"


def test_invalid_request_id_is_replaced(client: TestClient):
    """Test 4 - Invalid Request ID Is Replaced"""
    invalid_ids = [
        "invalid\nnewline",
        "invalid\rreturn",
        "invalid\x00null",
        "a" * 129,
        "",
        " ",
    ]
    for invalid_id in invalid_ids:
        response = client.get(
            "/api/v1/health/live", headers={"X-Request-ID": invalid_id}
        )
        assert response.status_code == 200
        req_id = response.headers.get("X-Request-ID")
        assert req_id is not None
        assert req_id != invalid_id
        uuid_obj = uuid.UUID(req_id)
        assert str(uuid_obj) == req_id


def test_contextvar_is_available_downstream(client: TestClient):
    """Test 5 - ContextVar Is Available Downstream"""
    response = client.get(
        "/api/v1/_test/request_id", headers={"X-Request-ID": "test-downstream-123"}
    )
    assert response.status_code == 200
    assert response.json()["request_id"] == "test-downstream-123"
    assert response.headers["X-Request-ID"] == "test-downstream-123"


def test_contextvar_is_reset(client: TestClient):
    """Test 6 - ContextVar Is Reset"""
    # Execute request
    response = client.get(
        "/api/v1/_test/request_id", headers={"X-Request-ID": "test-reset-123"}
    )
    assert response.status_code == 200

    # Outside the request context, it should be the default
    assert get_request_id() == "-"


def test_exception_cleanup(client: TestClient):
    """Test 7 - Exception Cleanup"""
    # The global exception handler converts this to 500
    response = client.get(
        "/api/v1/_test/exception", headers={"X-Request-ID": "test-error-123"}
    )
    assert response.status_code == 500

    # Should still be reset
    assert get_request_id() == "-"


def test_404_responses_also_receive_request_ids(client: TestClient):
    """Test 8 - 404 Responses Also Receive Request IDs"""
    response = client.get("/nonexistent-path")
    assert response.status_code == 404
    req_id = response.headers.get("X-Request-ID")
    assert req_id is not None
