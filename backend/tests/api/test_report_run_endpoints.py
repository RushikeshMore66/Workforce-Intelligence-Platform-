import os
import tempfile
from datetime import datetime, timedelta, timezone

import pytest

from app.models.report_run import ReportRunStatusEnum, TriggerTypeEnum
from app.models.report_schedule import ReportFormatEnum, ReportFrequencyEnum, ReportTypeEnum
from app.services.report_run_service import ReportRunService
from app.services.report_schedule_service import ReportScheduleService
from app.services.report_storage_service import ReportStorageService
from tests.test_report_execution import create_schedule

# We use the authenticated client and db_session from conftest.py

def create_schedule_for_api(db_session, owner_id):
    from app.schemas.report_schedules import ReportScheduleCreate
    
    sch_data = ReportScheduleCreate(
        name="Test API Schedule",
        report_type=ReportTypeEnum.ORGANIZATION,
        scope_id=None,
        export_format=ReportFormatEnum.CSV,
        frequency=ReportFrequencyEnum.DAILY,
        timezone="UTC",
        next_run_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    return ReportScheduleService(db_session).create_schedule(sch_data, owner_id)

@pytest.fixture
def test_schedule(db_session):
    return create_schedule_for_api(db_session, "usr-test-owner")


from app.auth.jwt import create_jwt_token
from app.models.user import User, UserRoleEnum

def auth(user_id: str, role: UserRoleEnum) -> dict:
    token = create_jwt_token(user_id, role.value).access_token
    return {"Authorization": f"Bearer {token}"}

OWNER = lambda: auth("usr-test-owner", UserRoleEnum.OWNER)
WORKER = lambda: auth("ex-worker-u", UserRoleEnum.WORKER)

@pytest.fixture(autouse=True)
def setup_worker(db_session):
    if not db_session.query(User).filter_by(id="ex-worker-u").first():
        worker_u = User(id="ex-worker-u", name="W", email="w@x.com", hashed_password="h",
                        role=UserRoleEnum.WORKER, avatar_initials="W")
        db_session.add(worker_u)
        db_session.commit()

class TestRunNowEndpoint:
    def test_owner_can_execute_active_schedule(self, client, test_schedule, db_session):
        response = client.post(
            f"/api/v1/reports/schedules/{test_schedule.id}/run-now",
            headers=OWNER()
        )
        assert response.status_code == 201
        data = response.json()
        
        assert data["trigger_type"] == "manual"
        assert data["scheduled_for"] is None
        
        # Verify next_run_at was not updated
        db_session.refresh(test_schedule)
        assert test_schedule.next_run_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)

    def test_non_owner_cannot_execute_schedule(self, client, test_schedule):
        response = client.post(
            f"/api/v1/reports/schedules/{test_schedule.id}/run-now",
            headers=WORKER()
        )
        assert response.status_code == 403

    def test_unauthenticated_user_cannot_execute(self, client, test_schedule):
        response = client.post(f"/api/v1/reports/schedules/{test_schedule.id}/run-now")
        assert response.status_code == 401

    def test_unknown_schedule_returns_404(self, client):
        response = client.post(
            "/api/v1/reports/schedules/sch_unknown/run-now",
            headers=OWNER()
        )
        assert response.status_code == 404

    def test_paused_schedule_returns_400(self, client, test_schedule, db_session):
        ReportScheduleService(db_session).pause_schedule(test_schedule.id)
        
        response = client.post(
            f"/api/v1/reports/schedules/{test_schedule.id}/run-now",
            headers=OWNER()
        )
        assert response.status_code == 400
        assert "paused" in response.json()["detail"].lower()

    def test_multiple_manual_calls_create_independent_runs(self, client, test_schedule):
        res1 = client.post(
            f"/api/v1/reports/schedules/{test_schedule.id}/run-now",
            headers=OWNER()
        )
        res2 = client.post(
            f"/api/v1/reports/schedules/{test_schedule.id}/run-now",
            headers=OWNER()
        )
        
        assert res1.status_code == 201
        assert res2.status_code == 201
        assert res1.json()["id"] != res2.json()["id"]


class TestDownloadEndpoint:
    @pytest.fixture
    def completed_run(self, db_session, test_schedule, tmp_path):
        import shutil
        from app.config import settings
        
        # Patch the base path to tmp_path for safe tests
        settings.REPORT_STORAGE_PATH = str(tmp_path)
        
        run = ReportRunService.create_manual_run(db_session, test_schedule.id)
        
        rel_path = f"organization/{test_schedule.id}/test_report.csv"
        abs_path = tmp_path / rel_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_text("id,name\n1,test")
        
        run.status = ReportRunStatusEnum.COMPLETED
        run.output_path = rel_path
        run.output_filename = "test_report.csv"
        db_session.commit()
        return run

    def test_owner_can_download_completed_report(self, client, completed_run):
        response = client.get(
            f"/api/v1/reports/runs/{completed_run.id}/download",
            headers=OWNER()
        )
        assert response.status_code == 200
        assert response.headers["content-disposition"] == 'attachment; filename="test_report.csv"'
        assert response.text.replace("\r\n", "\n") == "id,name\n1,test"

    def test_non_owner_cannot_download_report(self, client, completed_run):
        response = client.get(
            f"/api/v1/reports/runs/{completed_run.id}/download",
            headers=WORKER()
        )
        assert response.status_code == 403

    def test_unknown_run_returns_404(self, client):
        response = client.get(
            "/api/v1/reports/runs/run_unknown/download",
            headers=OWNER()
        )
        assert response.status_code == 404

    def test_pending_run_returns_400(self, client, db_session, test_schedule):
        run = ReportRunService.create_manual_run(db_session, test_schedule.id)
        db_session.commit() # Ensure it's committed!
        response = client.get(
            f"/api/v1/reports/runs/{run.id}/download",
            headers=OWNER()
        )
        assert response.status_code == 400
        assert "pending" in response.json()["detail"].lower()

    def test_completed_run_missing_file_returns_404(self, client, db_session, test_schedule):
        run = ReportRunService.create_manual_run(db_session, test_schedule.id)
        run.status = ReportRunStatusEnum.COMPLETED
        run.output_path = "does/not/exist.csv"
        db_session.commit()
        
        response = client.get(
            f"/api/v1/reports/runs/{run.id}/download",
            headers=OWNER()
        )
        assert response.status_code == 404

    def test_path_traversal_is_rejected(self, client, db_session, test_schedule):
        run = ReportRunService.create_manual_run(db_session, test_schedule.id)
        run.status = ReportRunStatusEnum.COMPLETED
        run.output_path = "../../../etc/passwd"
        db_session.commit()
        
        response = client.get(
            f"/api/v1/reports/runs/{run.id}/download",
            headers=OWNER()
        )
        assert response.status_code == 404
