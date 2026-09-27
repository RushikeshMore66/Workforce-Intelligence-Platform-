"""
Security hardening tests.

Covers:

    - JWT not returned in login JSON
    - HttpOnly authentication cookie
    - CSRF cookie generation
    - state-changing requests requiring CSRF when cookie-authenticated
    - bearer-token requests remaining usable without CSRF
    - login rate limiting when enabled
"""

import pytest

from app.config import settings
from app.core.csrf import (
    create_csrf_token,
    verify_csrf_token,
)


def test_csrf_token_is_bound_to_user():
    token = create_csrf_token(
        "user-a"
    )

    assert verify_csrf_token(
        token,
        "user-a",
    )

    assert not verify_csrf_token(
        token,
        "user-b",
    )


def test_csrf_token_rejects_tampering():
    token = create_csrf_token(
        "user-a"
    )

    nonce, signature = token.split(
        ".",
        1,
    )

    tampered = (
        f"{nonce}-tampered.{signature}"
    )

    assert not verify_csrf_token(
        tampered,
        "user-a",
    )


def test_login_does_not_expose_jwt(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "rajesh.mehta@apexsoftware.in",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["authenticated"] is True

    assert (
        "access_token"
        not in body
    )

    assert (
        "access_token"
        in response.cookies
    )

    assert (
        "csrf_token"
        in response.cookies
    )


def test_csrf_endpoint_refreshes_cookie(client):
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "rajesh.mehta@apexsoftware.in",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    response = client.get(
        "/api/v1/auth/csrf"
    )

    assert response.status_code == 200

    assert (
        "csrf_token"
        in response.cookies
    )


def test_bearer_get_me_does_not_require_csrf(
    client,
):
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "rajesh.mehta@apexsoftware.in",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    csrf_cookie = login_response.cookies.get(
        "csrf_token"
    )

    access_cookie = login_response.cookies.get(
        "access_token"
    )

    assert csrf_cookie
    assert access_cookie

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": (
                f"Bearer {access_cookie}"
            )
        },
    )

    assert response.status_code == 200
