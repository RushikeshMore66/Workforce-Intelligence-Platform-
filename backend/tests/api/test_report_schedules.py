import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth.jwt import create_jwt_token
from app.models.project import Project, ProjectHealthEnum, ProjectStatusEnum
from app.models.report_schedule import ReportFormatEnum, ReportFrequencyEnum, ReportTypeEnum, ReportSchedule
from app.models.report_run import ReportRun, ReportRunStatusEnum
from app.models.team import Team
from app.models.user import User, UserRoleEnum, Worker, WorkerStatusEnum


def auth(user_id: str, role: UserRoleEnum) -> dict:
    token = create_jwt_token(user_id, role.value).access_token
    return {"Authorization": f"Bearer {token}"}


OWNER = lambda: auth("usr-test-owner", UserRoleEnum.OWNER)
WORKER = lambda: auth("ex-worker-u", UserRoleEnum.WORKER)


@pytest.fixture
def schedule_data(db_session):
    for model in [ReportRun, ReportSchedule, Worker, Team, Project]:
        db_session.query(model).delete()
    db_session.query(User).filter(User.id != "usr-test-owner").delete()
    db_session.commit()

    worker_u = User(id="ex-worker-u", name="W", email="w@x.com", hashed_password="h",
                    role=UserRoleEnum.WORKER, avatar_initials="W")
    db_session.add(worker_u)
    db_session.commit()

    team = Team(id="ex-team", name="T", supervisor_id=None)
    db_session.add(team)
    
    worker = Worker(id="ex-worker", user_id="ex-worker-u", role="Dev", status=WorkerStatusEnum.ACTIVE)
    db_session.add(worker)
    
    project = Project(id="ex-project", name="P", client="C", start_date=datetime.now(), 
                      deadline=datetime.now(), status=ProjectStatusEnum.ACTIVE, health=ProjectHealthEnum.ON_TRACK)
    db_session.add(project)
    
    db_session.commit()


class TestReportSchedules:
    URL = "/api/v1/reports/schedules"

    def test_owner_can_create_org_schedule(self, client, schedule_data):
        payload = {
            "name": "Org Report",
            "report_type": "organization",
            "export_format": "pdf",
            "frequency": "weekly",
            "timezone": "UTC",
            "next_run_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }
        r = client.post(self.URL, json=payload, headers=OWNER())
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Org Report"
        assert data["is_active"] is True
        assert data["created_by_user_id"] == "usr-test-owner"

    def test_owner_can_create_project_schedule(self, client, schedule_data):
        payload = {
            "name": "Proj Report",
            "report_type": "project",
            "scope_id": "ex-project",
            "export_format": "csv",
            "frequency": "daily",
            "timezone": "America/New_York",
            "next_run_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }
        r = client.post(self.URL, json=payload, headers=OWNER())
        assert r.status_code == 201

    def test_create_project_schedule_missing_scope(self, client, schedule_data):
        payload = {
            "name": "Proj Report",
            "report_type": "project",
            "export_format": "csv",
            "frequency": "daily",
            "timezone": "America/New_York",
            "next_run_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }
        r = client.post(self.URL, json=payload, headers=OWNER())
        assert r.status_code == 400

    def test_create_worker_schedule_valid(self, client, schedule_data):
        payload = {
            "name": "Worker Report",
            "report_type": "worker",
            "scope_id": "ex-worker",
            "export_format": "xlsx",
            "frequency": "monthly",
            "timezone": "UTC",
            "next_run_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }
        r = client.post(self.URL, json=payload, headers=OWNER())
        assert r.status_code == 201

    def test_create_team_schedule_valid(self, client, schedule_data):
        payload = {
            "name": "Team Report",
            "report_type": "team",
            "scope_id": "ex-team",
            "export_format": "csv",
            "frequency": "daily",
            "timezone": "UTC",
            "next_run_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }
        r = client.post(self.URL, json=payload, headers=OWNER())
        assert r.status_code == 201

    def test_create_activity_schedule_valid_no_scope(self, client, schedule_data):
        payload = {
            "name": "Act Report",
            "report_type": "activity",
            "export_format": "csv",
            "frequency": "daily",
            "timezone": "UTC",
            "next_run_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }
        r = client.post(self.URL, json=payload, headers=OWNER())
        assert r.status_code == 201

    def test_create_activity_schedule_valid_with_scope(self, client, schedule_data):
        payload = {
            "name": "Act Report",
            "report_type": "activity",
            "scope_id": "ex-project",
            "export_format": "csv",
            "frequency": "daily",
            "timezone": "UTC",
            "next_run_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }
        r = client.post(self.URL, json=payload, headers=OWNER())
        assert r.status_code == 201

    def test_invalid_timezone(self, client, schedule_data):
        payload = {
            "name": "Org Report",
            "report_type": "organization",
            "export_format": "pdf",
            "frequency": "weekly",
            "timezone": "Invalid/Timezone",
            "next_run_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }
        r = client.post(self.URL, json=payload, headers=OWNER())
        assert r.status_code == 422

    def test_naive_datetime_rejected(self, client, schedule_data):
        payload = {
            "name": "Org Report",
            "report_type": "organization",
            "export_format": "pdf",
            "frequency": "weekly",
            "timezone": "UTC",
            "next_run_at": datetime.now().isoformat()
        }
        r = client.post(self.URL, json=payload, headers=OWNER())
        assert r.status_code == 422

    def test_invalid_report_type(self, client, schedule_data):
        payload = {
            "name": "Org Report",
            "report_type": "invalid",
            "export_format": "pdf",
            "frequency": "weekly",
            "timezone": "UTC",
            "next_run_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }
        r = client.post(self.URL, json=payload, headers=OWNER())
        assert r.status_code == 422

    def test_invalid_format(self, client, schedule_data):
        payload = {
            "name": "Org Report",
            "report_type": "organization",
            "export_format": "txt",
            "frequency": "weekly",
            "timezone": "UTC",
            "next_run_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }
        r = client.post(self.URL, json=payload, headers=OWNER())
        assert r.status_code == 422

    def test_worker_forbidden(self, client, schedule_data):
        payload = {
            "name": "Org Report",
            "report_type": "organization",
            "export_format": "pdf",
            "frequency": "weekly",
            "timezone": "UTC",
            "next_run_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }
        r = client.post(self.URL, json=payload, headers=WORKER())
        assert r.status_code == 403
        r = client.get(self.URL, headers=WORKER())
        assert r.status_code == 403
        r = client.get(f"{self.URL}/some-id", headers=WORKER())
        assert r.status_code == 403


class TestReportScheduleLifecycle:
    URL = "/api/v1/reports/schedules"

    @pytest.fixture
    def schedule(self, db_session, schedule_data):
        s = ReportSchedule(
            id="s1",
            name="S1",
            report_type=ReportTypeEnum.ORGANIZATION,
            export_format=ReportFormatEnum.CSV,
            frequency=ReportFrequencyEnum.DAILY,
            timezone="UTC",
            next_run_at=datetime.now(timezone.utc),
            is_active=True,
            created_by_user_id="usr-test-owner"
        )
        db_session.add(s)
        db_session.commit()
        return s

    def test_list_schedules(self, client, schedule):
        r = client.get(self.URL, headers=OWNER())
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_get_schedule(self, client, schedule):
        r = client.get(f"{self.URL}/{schedule.id}", headers=OWNER())
        assert r.status_code == 200
        assert r.json()["id"] == schedule.id

    def test_update_schedule(self, client, schedule):
        r = client.patch(f"{self.URL}/{schedule.id}", json={"name": "S1 Updated"}, headers=OWNER())
        assert r.status_code == 200
        assert r.json()["name"] == "S1 Updated"
        # ensure ID and creator preserved
        assert r.json()["id"] == schedule.id
        assert r.json()["created_by_user_id"] == "usr-test-owner"

    def test_pause_resume(self, client, schedule):
        r = client.post(f"{self.URL}/{schedule.id}/pause", headers=OWNER())
        assert r.status_code == 200
        assert r.json()["is_active"] is False

        # Idempotent
        r = client.post(f"{self.URL}/{schedule.id}/pause", headers=OWNER())
        assert r.status_code == 200
        assert r.json()["is_active"] is False

        r = client.post(f"{self.URL}/{schedule.id}/resume", headers=OWNER())
        assert r.status_code == 200
        assert r.json()["is_active"] is True

        # Idempotent
        r = client.post(f"{self.URL}/{schedule.id}/resume", headers=OWNER())
        assert r.status_code == 200
        assert r.json()["is_active"] is True

    def test_delete_schedule(self, client, db_session, schedule):
        # Create a run to test cascade
        run = ReportRun(id="r1", schedule_id=schedule.id, status=ReportRunStatusEnum.PENDING)
        db_session.add(run)
        db_session.commit()

        r = client.delete(f"{self.URL}/{schedule.id}", headers=OWNER())
        assert r.status_code == 204

        # Schedule deleted
        r = client.get(f"{self.URL}/{schedule.id}", headers=OWNER())
        assert r.status_code == 404

        # Run cascaded
        assert db_session.query(ReportRun).filter_by(id="r1").first() is None


class TestReportRuns:
    @pytest.fixture
    def schedule(self, db_session):
        db_session.query(ReportRun).delete()
        db_session.query(ReportSchedule).delete()
        db_session.commit()
        s = ReportSchedule(
            id="s1",
            name="S1",
            report_type=ReportTypeEnum.ORGANIZATION,
            export_format=ReportFormatEnum.CSV,
            frequency=ReportFrequencyEnum.DAILY,
            timezone="UTC",
            next_run_at=datetime.now(timezone.utc),
            is_active=True
        )
        db_session.add(s)
        
        runs = []
        for i in range(55):
            run = ReportRun(
                id=f"run-{i}",
                schedule_id="s1",
                status=ReportRunStatusEnum.COMPLETED,
                created_at=datetime.now() - timedelta(minutes=i)
            )
            runs.append(run)
        db_session.add_all(runs)
        db_session.commit()
        return s

    def test_list_runs_limit_and_order(self, client, schedule):
        r = client.get(f"/api/v1/reports/schedules/{schedule.id}/runs", headers=OWNER())
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 50
        
        # Newest first: created_at of item 0 > item 1
        t0 = datetime.fromisoformat(data[0]["created_at"])
        t1 = datetime.fromisoformat(data[1]["created_at"])
        assert t0 > t1

    def test_get_run(self, client, schedule):
        r = client.get(f"/api/v1/reports/runs/run-0", headers=OWNER())
        assert r.status_code == 200
        assert r.json()["id"] == "run-0"

    def test_get_unknown_run(self, client, schedule):
        r = client.get(f"/api/v1/reports/runs/unknown", headers=OWNER())
        assert r.status_code == 404
