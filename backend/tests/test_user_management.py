"""
Tests for User & Account Management lifecycle.

NOTE: Test client responses contain snake_case keys (backend Pydantic output).
The camelCase transform only happens in the frontend API client (lib/api/client.ts).
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRoleEnum, Supervisor, TeamLeader, Worker
from app.models.team import Team
from app.auth.jwt import create_jwt_token
from app.core.security import get_password_hash

# Isolated database for user management tests
UM_DB_URL = "sqlite:///./test_user_mgmt.db"
um_engine = create_engine(UM_DB_URL, connect_args={"check_same_thread": False})
UMSession = sessionmaker(autocommit=False, autoflush=False, bind=um_engine)


def make_token(user_id: str, role: str) -> str:
    return create_jwt_token(user_id=user_id, role=role).access_token


def auth_header(user_id: str, role: str) -> dict:
    return {"Authorization": f"Bearer {make_token(user_id, role)}"}


@pytest.fixture(scope="module")
def um_db():
    Base.metadata.create_all(bind=um_engine)
    db = UMSession()

    # Owner user
    owner = User(
        id="um-owner-1",
        name="Test Owner",
        email="owner@umtest.com",
        hashed_password=get_password_hash("password123"),
        role=UserRoleEnum.OWNER,
        avatar_initials="TO",
        is_active=True,
    )
    sup_user = User(
        id="um-sup-user",
        name="Sup User",
        email="sup@umtest.com",
        hashed_password=get_password_hash("password123"),
        role=UserRoleEnum.SUPERVISOR,
        avatar_initials="SU",
        is_active=True,
    )
    worker_user = User(
        id="um-worker-user",
        name="Worker User",
        email="worker@umtest.com",
        hashed_password=get_password_hash("password123"),
        role=UserRoleEnum.WORKER,
        avatar_initials="WU",
        is_active=True,
    )
    deactivated_user = User(
        id="um-deact-user",
        name="Deactivated User",
        email="deact@umtest.com",
        hashed_password=get_password_hash("password123"),
        role=UserRoleEnum.WORKER,
        avatar_initials="DU",
        is_active=False,
    )

    for u in [owner, sup_user, worker_user, deactivated_user]:
        db.add(u)
    db.flush()

    sup_profile = Supervisor(id="um-sup-profile", user_id="um-sup-user")
    db.add(sup_profile)
    db.flush()

    # Team managed by supervisor
    team = Team(id="um-team-1", name="UM Test Team", supervisor_id="um-sup-profile")
    db.add(team)
    db.flush()

    tl_user = User(
        id="um-tl-user",
        name="TL User",
        email="tl@umtest.com",
        hashed_password=get_password_hash("password123"),
        role=UserRoleEnum.TEAM_LEADER,
        avatar_initials="TL",
        is_active=True,
    )
    db.add(tl_user)
    db.flush()

    tl_profile = TeamLeader(id="um-tl-profile", user_id="um-tl-user", team_id="um-team-1")
    db.add(tl_profile)

    worker_profile = Worker(
        id="um-worker-profile",
        user_id="um-worker-user",
        role="Developer",
        team_id="um-team-1",
        team_leader_id="um-tl-profile",
        supervisor_id="um-sup-profile",
        status="ACTIVE",
    )
    db.add(worker_profile)

    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=um_engine)


@pytest.fixture
def um_client(um_db):
    db = UMSession()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    db.close()


# ─────────────────────────────────────────────
# Authentication hardening: is_active check
# ─────────────────────────────────────────────

class TestDeactivatedUserAuth:
    def test_deactivated_user_cannot_login(self, um_client):
        """A user with is_active=False must receive 401 on login."""
        resp = um_client.post(
            "/api/v1/auth/login",
            json={"email": "deact@umtest.com", "password": "password123"},
        )
        assert resp.status_code == 401

    def test_active_user_can_login(self, um_client):
        """A user with is_active=True can login normally."""
        resp = um_client.post(
            "/api/v1/auth/login",
            json={"email": "owner@umtest.com", "password": "password123"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_deactivated_token_rejected_on_me(self, um_client):
        """Even if a deactivated user holds a valid JWT, /auth/me must return 401."""
        token = make_token("um-deact-user", "WORKER")
        resp = um_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401


# ─────────────────────────────────────────────
# GET /auth/me profile IDs
# ─────────────────────────────────────────────

class TestAuthMe:
    def test_me_returns_worker_profile_id(self, um_client):
        token = make_token("um-worker-user", "WORKER")
        resp = um_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        # Backend returns snake_case keys
        assert data["worker_profile_id"] == "um-worker-profile"
        assert data["is_active"] is True

    def test_me_returns_supervisor_profile_id(self, um_client):
        token = make_token("um-sup-user", "SUPERVISOR")
        resp = um_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["supervisor_profile_id"] == "um-sup-profile"


# ─────────────────────────────────────────────
# RBAC: only OWNER can access /users
# ─────────────────────────────────────────────

class TestUserManagementRBAC:
    def test_worker_cannot_list_users(self, um_client):
        resp = um_client.get(
            "/api/v1/users",
            headers=auth_header("um-worker-user", "WORKER"),
        )
        assert resp.status_code == 403

    def test_supervisor_cannot_list_users(self, um_client):
        resp = um_client.get(
            "/api/v1/users",
            headers=auth_header("um-sup-user", "SUPERVISOR"),
        )
        assert resp.status_code == 403

    def test_team_leader_cannot_list_users(self, um_client):
        resp = um_client.get(
            "/api/v1/users",
            headers=auth_header("um-tl-user", "TEAM_LEADER"),
        )
        assert resp.status_code == 403

    def test_owner_can_list_users(self, um_client):
        resp = um_client.get(
            "/api/v1/users",
            headers=auth_header("um-owner-1", "OWNER"),
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_unauthenticated_cannot_access_users(self, um_client):
        resp = um_client.get("/api/v1/users")
        assert resp.status_code == 401


# ─────────────────────────────────────────────
# Create user
# ─────────────────────────────────────────────

class TestCreateUser:
    def test_owner_can_create_supervisor(self, um_client):
        resp = um_client.post(
            "/api/v1/users",
            json={
                "email": "newsup@umtest.com",
                "name": "New Supervisor",
                "password": "securepass1",
                "role": "SUPERVISOR",
            },
            headers=auth_header("um-owner-1", "OWNER"),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "newsup@umtest.com"
        assert data["role"] == "SUPERVISOR"
        assert data["is_active"] is True
        assert data["supervisor_profile_id"] is not None
        # Must NOT expose hashed_password
        assert "hashed_password" not in data

    def test_owner_can_create_team_leader_with_team(self, um_client):
        # Create a dedicated team for this test (um-team-1 already has a leader)
        db = UMSession()
        tl_test_team = Team(id="um-tl-test-team", name="TL Test Team UM", supervisor_id=None)
        db.add(tl_test_team)
        db.commit()
        db.close()

        resp = um_client.post(
            "/api/v1/users",
            json={
                "email": "newtl@umtest.com",
                "name": "New TL",
                "password": "securepass1",
                "role": "TEAM_LEADER",
                "team_leader_profile": {"team_id": "um-tl-test-team"},
            },
            headers=auth_header("um-owner-1", "OWNER"),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["team_leader_profile_id"] is not None

    def test_owner_can_create_worker_with_profile(self, um_client):
        resp = um_client.post(
            "/api/v1/users",
            json={
                "email": "newworker@umtest.com",
                "name": "New Worker",
                "password": "securepass1",
                "role": "WORKER",
                "worker_profile": {
                    "job_title": "Backend Engineer",
                    "team_id": "um-team-1",
                    "team_leader_id": "um-tl-profile",
                    "supervisor_id": "um-sup-profile",
                    "status": "ACTIVE",
                },
            },
            headers=auth_header("um-owner-1", "OWNER"),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["worker_profile_id"] is not None

    def test_duplicate_email_rejected(self, um_client):
        resp = um_client.post(
            "/api/v1/users",
            json={
                "email": "owner@umtest.com",  # already exists
                "name": "Duplicate",
                "password": "securepass1",
                "role": "SUPERVISOR",
            },
            headers=auth_header("um-owner-1", "OWNER"),
        )
        assert resp.status_code == 409

    def test_cannot_create_owner_role(self, um_client):
        resp = um_client.post(
            "/api/v1/users",
            json={
                "email": "newowner@umtest.com",
                "name": "New Owner",
                "password": "securepass1",
                "role": "OWNER",
            },
            headers=auth_header("um-owner-1", "OWNER"),
        )
        assert resp.status_code == 403

    def test_worker_without_profile_rejected(self, um_client):
        resp = um_client.post(
            "/api/v1/users",
            json={
                "email": "noProfile@umtest.com",
                "name": "No Profile Worker",
                "password": "securepass1",
                "role": "WORKER",
                # No worker_profile provided
            },
            headers=auth_header("um-owner-1", "OWNER"),
        )
        assert resp.status_code == 400

    def test_invalid_team_rejected(self, um_client):
        resp = um_client.post(
            "/api/v1/users",
            json={
                "email": "badteam@umtest.com",
                "name": "Bad Team Worker",
                "password": "securepass1",
                "role": "WORKER",
                "worker_profile": {
                    "job_title": "QA",
                    "team_id": "nonexistent-team",
                    "status": "ACTIVE",
                },
            },
            headers=auth_header("um-owner-1", "OWNER"),
        )
        assert resp.status_code == 400

    def test_mismatched_team_leader_rejected(self, um_client):
        """Team leader must lead the same team as the worker's team."""
        # Create a second team with no supervisor
        db = UMSession()
        other_team = Team(id="um-other-team", name="Other Team UM", supervisor_id=None)
        db.add(other_team)
        db.commit()
        db.close()

        resp = um_client.post(
            "/api/v1/users",
            json={
                "email": "mismatch@umtest.com",
                "name": "Mismatch Worker",
                "password": "securepass1",
                "role": "WORKER",
                "worker_profile": {
                    "job_title": "Dev",
                    "team_id": "um-other-team",
                    "team_leader_id": "um-tl-profile",  # leads um-team-1, not um-other-team
                    "status": "ACTIVE",
                },
            },
            headers=auth_header("um-owner-1", "OWNER"),
        )
        assert resp.status_code == 400

    def test_short_password_rejected(self, um_client):
        resp = um_client.post(
            "/api/v1/users",
            json={
                "email": "short@umtest.com",
                "name": "Short Password",
                "password": "123",
                "role": "SUPERVISOR",
            },
            headers=auth_header("um-owner-1", "OWNER"),
        )
        assert resp.status_code == 422


# ─────────────────────────────────────────────
# Activate / Deactivate
# ─────────────────────────────────────────────

class TestUserLifecycle:
    def test_owner_can_deactivate_user(self, um_client):
        resp = um_client.post(
            "/api/v1/users/um-worker-user/deactivate",
            headers=auth_header("um-owner-1", "OWNER"),
        )
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

    def test_deactivated_user_cannot_login_after_deactivation(self, um_client):
        resp = um_client.post(
            "/api/v1/auth/login",
            json={"email": "worker@umtest.com", "password": "password123"},
        )
        assert resp.status_code == 401

    def test_owner_can_reactivate_user(self, um_client):
        resp = um_client.post(
            "/api/v1/users/um-worker-user/activate",
            headers=auth_header("um-owner-1", "OWNER"),
        )
        assert resp.status_code == 200
        assert resp.json()["is_active"] is True

    def test_reactivated_user_can_login(self, um_client):
        resp = um_client.post(
            "/api/v1/auth/login",
            json={"email": "worker@umtest.com", "password": "password123"},
        )
        assert resp.status_code == 200

    def test_cannot_deactivate_self(self, um_client):
        resp = um_client.post(
            "/api/v1/users/um-owner-1/deactivate",
            headers=auth_header("um-owner-1", "OWNER"),
        )
        assert resp.status_code == 400

    def test_non_owner_cannot_deactivate(self, um_client):
        resp = um_client.post(
            "/api/v1/users/um-worker-user/deactivate",
            headers=auth_header("um-worker-user", "WORKER"),
        )
        assert resp.status_code == 403


# ─────────────────────────────────────────────
# Profile update (self)
# ─────────────────────────────────────────────

class TestProfileUpdate:
    def test_user_can_update_own_name(self, um_client):
        token = make_token("um-sup-user", "SUPERVISOR")
        resp = um_client.patch(
            "/api/v1/auth/me",
            json={"name": "Updated Supervisor Name"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Supervisor Name"

    def test_user_can_update_own_company(self, um_client):
        token = make_token("um-owner-1", "OWNER")
        resp = um_client.patch(
            "/api/v1/auth/me",
            json={"company": "New Company Ltd"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["company"] == "New Company Ltd"

    def test_user_cannot_change_own_role_via_profile(self, um_client):
        """Role is not a field in UpdateProfileRequest — backend ignores/rejects it."""
        token = make_token("um-sup-user", "SUPERVISOR")
        resp = um_client.patch(
            "/api/v1/auth/me",
            json={"role": "OWNER"},
            headers={"Authorization": f"Bearer {token}"},
        )
        # Either 200 (role ignored) or 422 (validation error). Role must not change.
        if resp.status_code == 200:
            assert resp.json()["role"] == "SUPERVISOR"

    def test_unauthenticated_profile_update_fails(self, um_client):
        resp = um_client.patch(
            "/api/v1/auth/me",
            json={"name": "Hacker"},
        )
        assert resp.status_code == 401


# ─────────────────────────────────────────────
# Change password
# ─────────────────────────────────────────────

class TestChangePassword:
    def test_correct_current_password_accepted(self, um_client):
        token = make_token("um-owner-1", "OWNER")
        resp = um_client.post(
            "/api/v1/auth/change-password",
            # Backend expects snake_case field names
            json={"current_password": "password123", "new_password": "newpassword456"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 204

    def test_new_password_works_after_change(self, um_client):
        resp = um_client.post(
            "/api/v1/auth/login",
            json={"email": "owner@umtest.com", "password": "newpassword456"},
        )
        assert resp.status_code == 200

    def test_old_password_rejected_after_change(self, um_client):
        resp = um_client.post(
            "/api/v1/auth/login",
            json={"email": "owner@umtest.com", "password": "password123"},
        )
        assert resp.status_code == 401

    def test_incorrect_current_password_rejected(self, um_client):
        token = make_token("um-sup-user", "SUPERVISOR")
        resp = um_client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "wrongpassword", "new_password": "newpass789"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400

    def test_short_new_password_rejected(self, um_client):
        token = make_token("um-sup-user", "SUPERVISOR")
        resp = um_client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "password123", "new_password": "short"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

