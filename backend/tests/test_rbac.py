import hashlib
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRoleEnum, Supervisor, TeamLeader, Worker
from app.models.team import Team
from app.models.notification import Notification
from app.auth.jwt import create_jwt_token
from app.core.security import get_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Separate in-memory DB for authorization tests
RBAC_DB_URL = "sqlite:///./test_rbac.db"

rbac_engine = create_engine(RBAC_DB_URL, connect_args={"check_same_thread": False})
RBACSession = sessionmaker(autocommit=False, autoflush=False, bind=rbac_engine)




def make_token(user_id: str, role: str) -> str:
    return create_jwt_token(user_id=user_id, role=role).access_token


@pytest.fixture(scope="module")
def rbac_db():
    Base.metadata.create_all(bind=rbac_engine)
    db = RBACSession()

    # Users
    owner_user = User(
        id="rbac-owner",
        name="Owner User",
        email="owner@test.com",
        hashed_password=get_password_hash("pass"),
        role=UserRoleEnum.OWNER,
        avatar_initials="OW",
    )
    sup_user = User(
        id="rbac-sup",
        name="Supervisor User",
        email="sup@test.com",
        hashed_password=get_password_hash("pass"),
        role=UserRoleEnum.SUPERVISOR,
        avatar_initials="SU",
    )
    leader_user = User(
        id="rbac-leader",
        name="Leader User",
        email="leader@test.com",
        hashed_password=get_password_hash("pass"),
        role=UserRoleEnum.TEAM_LEADER,
        avatar_initials="LU",
    )
    worker_user = User(
        id="rbac-worker",
        name="Worker User",
        email="worker@test.com",
        hashed_password=get_password_hash("pass"),
        role=UserRoleEnum.WORKER,
        avatar_initials="WU",
    )
    other_worker_user = User(
        id="rbac-other-worker",
        name="Other Worker",
        email="otherworker@test.com",
        hashed_password=get_password_hash("pass"),
        role=UserRoleEnum.WORKER,
        avatar_initials="OW",
    )

    for u in [owner_user, sup_user, leader_user, worker_user, other_worker_user]:
        db.add(u)
    db.flush()

    supervisor = Supervisor(id="sup-profile-1", user_id="rbac-sup")
    db.add(supervisor)
    db.flush()

    team = Team(id="team-rbac-1", name="RBAC Test Team", supervisor_id="sup-profile-1")
    db.add(team)
    db.flush()

    leader = TeamLeader(id="leader-profile-1", user_id="rbac-leader", team_id="team-rbac-1")
    db.add(leader)
    db.flush()

    worker = Worker(
        id="worker-profile-1",
        user_id="rbac-worker",
        role="Developer",
        team_id="team-rbac-1",
        team_leader_id="leader-profile-1",
        supervisor_id="sup-profile-1",
        status="ACTIVE",
    )
    other_worker = Worker(
        id="worker-profile-2",
        user_id="rbac-other-worker",
        role="QA",
        team_id=None,  # belongs to no team
        status="ACTIVE",
    )
    db.add(worker)
    db.add(other_worker)

    # Notification belonging to worker
    notif = Notification(
        id="notif-worker-1",
        user_id="rbac-worker",
        type="SYSTEM",
        title="Test",
        description="Test notification",
        priority="LOW",
        read=False,
    )
    db.add(notif)

    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=rbac_engine)


@pytest.fixture
def rbac_client(rbac_db):
    db = RBACSession()

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


def auth_header(user_id: str, role: str) -> dict:
    token = make_token(user_id, role)
    return {"Authorization": f"Bearer {token}"}


# ─────────────────────────────────────────────
# Authentication tests (no token → 401)
# ─────────────────────────────────────────────

class TestAuthentication:
    def test_missing_token_returns_401_on_projects(self, rbac_client):
        resp = rbac_client.get("/api/v1/projects")
        assert resp.status_code == 401

    def test_missing_token_returns_401_on_workers(self, rbac_client):
        resp = rbac_client.get("/api/v1/workers")
        assert resp.status_code == 401

    def test_missing_token_returns_401_on_teams(self, rbac_client):
        resp = rbac_client.get("/api/v1/teams")
        assert resp.status_code == 401

    def test_missing_token_returns_401_on_analytics(self, rbac_client):
        resp = rbac_client.get("/api/v1/analytics")
        assert resp.status_code == 401

    def test_invalid_token_returns_401(self, rbac_client):
        resp = rbac_client.get(
            "/api/v1/projects",
            headers={"Authorization": "Bearer thisisnotavalidtoken"},
        )
        assert resp.status_code == 401

    def test_missing_token_returns_401_on_auth_me(self, rbac_client):
        resp = rbac_client.get("/api/v1/auth/me")
        assert resp.status_code == 401


# ─────────────────────────────────────────────
# Role authorization tests (wrong role → 403)
# ─────────────────────────────────────────────

class TestRoleAuthorization:
    def test_worker_cannot_create_project(self, rbac_client):
        resp = rbac_client.post(
            "/api/v1/projects",
            json={
                "name": "Illegal Project",
                "client": "Hack",
                "start_date": "2026-01-01",
                "deadline": "2026-12-31",
                "priority": "LOW",
            },
            headers=auth_header("rbac-worker", "WORKER"),
        )
        assert resp.status_code == 403

    def test_team_leader_cannot_create_project(self, rbac_client):
        resp = rbac_client.post(
            "/api/v1/projects",
            json={
                "name": "Illegal Project TL",
                "client": "Hack",
                "start_date": "2026-01-01",
                "deadline": "2026-12-31",
                "priority": "LOW",
            },
            headers=auth_header("rbac-leader", "TEAM_LEADER"),
        )
        assert resp.status_code == 403

    def test_worker_cannot_access_analytics(self, rbac_client):
        resp = rbac_client.get(
            "/api/v1/analytics",
            headers=auth_header("rbac-worker", "WORKER"),
        )
        assert resp.status_code == 403

    def test_team_leader_cannot_access_analytics(self, rbac_client):
        resp = rbac_client.get(
            "/api/v1/analytics",
            headers=auth_header("rbac-leader", "TEAM_LEADER"),
        )
        assert resp.status_code == 403

    def test_worker_cannot_create_task(self, rbac_client):
        resp = rbac_client.post(
            "/api/v1/tasks",
            json={
                "project_id": "proj-x",
                "title": "Illegal Task",
                "due_date": "2026-12-31",
            },
            headers=auth_header("rbac-worker", "WORKER"),
        )
        assert resp.status_code == 403


# ─────────────────────────────────────────────
# Resource-level scoping tests
# ─────────────────────────────────────────────

class TestResourceScoping:
    def test_worker_sees_only_own_profile_in_worker_list(self, rbac_client):
        resp = rbac_client.get(
            "/api/v1/workers",
            headers=auth_header("rbac-worker", "WORKER"),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == "worker-profile-1"

    def test_worker_cannot_access_other_workers_profile(self, rbac_client):
        # "other worker" has no team and no relation to rbac-worker
        resp = rbac_client.get(
            "/api/v1/workers/worker-profile-2",
            headers=auth_header("rbac-worker", "WORKER"),
        )
        assert resp.status_code == 403

    def test_owner_can_list_all_workers(self, rbac_client):
        resp = rbac_client.get(
            "/api/v1/workers",
            headers=auth_header("rbac-owner", "OWNER"),
        )
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    def test_worker_sees_only_own_team(self, rbac_client):
        resp = rbac_client.get(
            "/api/v1/teams",
            headers=auth_header("rbac-worker", "WORKER"),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == "team-rbac-1"

    def test_team_leader_sees_only_own_team(self, rbac_client):
        resp = rbac_client.get(
            "/api/v1/teams",
            headers=auth_header("rbac-leader", "TEAM_LEADER"),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == "team-rbac-1"

    def test_supervisor_sees_only_assigned_teams(self, rbac_client):
        resp = rbac_client.get(
            "/api/v1/teams",
            headers=auth_header("rbac-sup", "SUPERVISOR"),
        )
        assert resp.status_code == 200
        data = resp.json()
        # Only the team assigned to this supervisor
        team_ids = {t["id"] for t in data}
        assert "team-rbac-1" in team_ids

    def test_owner_sees_all_teams(self, rbac_client):
        resp = rbac_client.get(
            "/api/v1/teams",
            headers=auth_header("rbac-owner", "OWNER"),
        )
        assert resp.status_code == 200


# ─────────────────────────────────────────────
# IDOR prevention tests
# ─────────────────────────────────────────────

class TestIDORPrevention:
    def test_notification_idor_worker_cannot_read_others(self, rbac_client):
        """Worker cannot mark another user's notification as read."""
        # The notification "notif-worker-1" belongs to rbac-worker.
        # rbac-other-worker should not be able to read it.
        resp = rbac_client.patch(
            "/api/v1/notifications/notif-worker-1/read",
            headers=auth_header("rbac-other-worker", "WORKER"),
        )
        assert resp.status_code == 403

    def test_notification_owner_can_mark_read(self, rbac_client):
        """The notification owner can mark their notification as read."""
        resp = rbac_client.patch(
            "/api/v1/notifications/notif-worker-1/read",
            headers=auth_header("rbac-worker", "WORKER"),
        )
        assert resp.status_code == 200


# ─────────────────────────────────────────────
# Owner access tests
# ─────────────────────────────────────────────

class TestOwnerAccess:
    def test_owner_can_access_analytics(self, rbac_client):
        resp = rbac_client.get(
            "/api/v1/analytics",
            headers=auth_header("rbac-owner", "OWNER"),
        )
        assert resp.status_code == 200

    def test_owner_can_list_workers(self, rbac_client):
        resp = rbac_client.get(
            "/api/v1/workers",
            headers=auth_header("rbac-owner", "OWNER"),
        )
        assert resp.status_code == 200

    def test_owner_can_access_notifications(self, rbac_client):
        resp = rbac_client.get(
            "/api/v1/notifications",
            headers=auth_header("rbac-owner", "OWNER"),
        )
        assert resp.status_code == 200


# ─────────────────────────────────────────────
# Public endpoints (no auth required)
# ─────────────────────────────────────────────

class TestPublicEndpoints:
    def test_health_check_is_public(self, rbac_client):
        resp = rbac_client.get("/health")
        assert resp.status_code == 200

    def test_login_is_public(self, rbac_client):
        # Login with invalid creds should 401 (auth error), not forbidden
        resp = rbac_client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "wrong"},
        )
        assert resp.status_code == 401
