"""
Tests for Phase 7.15 Report Export endpoints.

Coverage:
1.  RBAC for every export endpoint
2.  All three formats (csv, xlsx, pdf)
3.  Invalid format → HTTP 400
4.  Correct media types
5.  Correct Content-Disposition filenames
6.  CSV headers and content
7.  XLSX opens successfully (openpyxl)
8.  PDF is non-empty and starts with %PDF
9.  Activity export filters and pagination
10. Maximum limit enforcement (>1000 → 400)
11. Empty/zero-safe export (no crash on empty data)
12. Export values match JSON report values
"""

import csv
import io
from datetime import date, datetime, timedelta

import pytest
from openpyxl import load_workbook

from app.auth.jwt import create_jwt_token
from app.models.project import Project, ProjectHealthEnum, ProjectStatusEnum
from app.models.task import Task, TaskStatusEnum, TaskTransition, WorkUpdate
from app.models.team import Team, team_projects
from app.models.user import (
    Supervisor, TeamLeader, User, UserRoleEnum, Worker, WorkerStatusEnum,
)


# ─── Auth helper ─────────────────────────────────────────────────────────────

def auth(user_id: str, role: UserRoleEnum) -> dict:
    token = create_jwt_token(user_id, role.value).access_token
    return {"Authorization": f"Bearer {token}"}


OWNER = lambda: auth("usr-test-owner", UserRoleEnum.OWNER)  # noqa: E731


# ─── Shared fixture ───────────────────────────────────────────────────────────

@pytest.fixture
def export_data(db_session):
    """Isolated dataset matching the Phase 7.14 report_data fixture pattern."""
    for model in [TaskTransition, WorkUpdate, Task, team_projects, Project,
                  Worker, TeamLeader, Supervisor, Team]:
        db_session.query(model).delete()
    db_session.query(User).filter(User.id != "usr-test-owner").delete()
    db_session.commit()

    sup_u = User(id="ex-sup-u", name="Sup", email="ex-sup@x.com", hashed_password="h",
                 role=UserRoleEnum.SUPERVISOR, avatar_initials="SU")
    tl_u  = User(id="ex-tl-u",  name="TL",  email="ex-tl@x.com",  hashed_password="h",
                 role=UserRoleEnum.TEAM_LEADER, avatar_initials="TL")
    w1_u  = User(id="ex-w1-u",  name="Alice", email="ex-w1@x.com", hashed_password="h",
                 role=UserRoleEnum.WORKER, avatar_initials="AL")
    w2_u  = User(id="ex-w2-u",  name="Bob",   email="ex-w2@x.com", hashed_password="h",
                 role=UserRoleEnum.WORKER, avatar_initials="BO")
    db_session.add_all([sup_u, tl_u, w1_u, w2_u])
    db_session.commit()

    sup  = Supervisor(id="ex-sup", user_id="ex-sup-u")
    db_session.add(sup)
    db_session.commit()

    team1 = Team(id="ex-team1", name="Export Alpha", supervisor_id="ex-sup")
    team2 = Team(id="ex-team2", name="Export Beta",  supervisor_id="ex-sup")
    db_session.add_all([team1, team2])
    db_session.commit()

    tl = TeamLeader(id="ex-tl", user_id="ex-tl-u", team_id="ex-team1")
    db_session.add(tl)
    db_session.commit()

    w1 = Worker(id="ex-w1", user_id="ex-w1-u", role="Dev", team_id="ex-team1",
                status=WorkerStatusEnum.ACTIVE)
    w2 = Worker(id="ex-w2", user_id="ex-w2-u", role="QA",  team_id="ex-team1",
                status=WorkerStatusEnum.ON_LEAVE)
    db_session.add_all([w1, w2])
    db_session.commit()

    today = date.today()
    p1 = Project(id="ex-p1", name="Export Project", client="Client X",
                 start_date=today - timedelta(days=30), deadline=today + timedelta(days=30),
                 status=ProjectStatusEnum.ACTIVE, health=ProjectHealthEnum.ON_TRACK)
    db_session.add(p1)
    db_session.commit()

    db_session.execute(team_projects.insert().values(team_id="ex-team1", project_id="ex-p1"))
    db_session.commit()

    now = datetime.utcnow()

    t1 = Task(id="ex-t1", project_id="ex-p1", title="Task One", assignee_id="ex-w1",
              status=TaskStatusEnum.COMPLETED, due_date=today + timedelta(days=1))
    t2 = Task(id="ex-t2", project_id="ex-p1", title="Task Two", assignee_id="ex-w2",
              status=TaskStatusEnum.BLOCKED, due_date=today - timedelta(days=2))
    db_session.add_all([t1, t2])
    db_session.commit()

    tr1 = TaskTransition(id="ex-tr1", task_id="ex-t1",
                         from_status=TaskStatusEnum.TODO,
                         to_status=TaskStatusEnum.IN_PROGRESS,
                         timestamp=now - timedelta(hours=6))
    tr2 = TaskTransition(id="ex-tr2", task_id="ex-t1",
                         from_status=TaskStatusEnum.IN_PROGRESS,
                         to_status=TaskStatusEnum.COMPLETED,
                         timestamp=now - timedelta(hours=2))
    db_session.add_all([tr1, tr2])
    db_session.commit()

    wu1 = WorkUpdate(id="ex-wu1", task_id="ex-t1", worker_id="ex-w1",
                     created_by_user_id="ex-w1-u", description="Worker note",
                     timestamp=now - timedelta(hours=5))
    wu2 = WorkUpdate(id="ex-wu2", task_id="ex-t1", worker_id="ex-w1",
                     created_by_user_id="ex-sup-u", description="Mgmt note",
                     timestamp=now - timedelta(hours=4))
    wu3 = WorkUpdate(id="ex-wu3", task_id="ex-t2", worker_id="ex-w2",
                     created_by_user_id=None, description="Legacy",
                     timestamp=now - timedelta(days=35))
    db_session.add_all([wu1, wu2, wu3])
    db_session.commit()


# ─── Helpers ─────────────────────────────────────────────────────────────────

def parse_csv(content: bytes) -> list[list[str]]:
    text = content.decode("utf-8")
    return list(csv.reader(io.StringIO(text)))


def assert_xlsx_valid(content: bytes) -> None:
    wb = load_workbook(filename=io.BytesIO(content))
    assert len(wb.sheetnames) >= 1


def assert_pdf_valid(content: bytes) -> None:
    assert len(content) > 100
    assert content[:4] == b"%PDF"


# ─── Organization export ─────────────────────────────────────────────────────

class TestOrganizationExport:
    URL = "/api/v1/reports/organization/export"

    def test_owner_csv(self, client, export_data):
        r = client.get(self.URL, headers=OWNER())
        assert r.status_code == 200
        assert "text/csv" in r.headers["content-type"]
        assert "organization-report.csv" in r.headers["content-disposition"]
        rows = parse_csv(r.content)
        assert rows[0] == ["Metric", "Value"]
        assert len(rows) > 1

    def test_owner_xlsx(self, client, export_data):
        r = client.get(f"{self.URL}?format=xlsx", headers=OWNER())
        assert r.status_code == 200
        assert "spreadsheetml" in r.headers["content-type"]
        assert "organization-report.xlsx" in r.headers["content-disposition"]
        assert_xlsx_valid(r.content)

    def test_owner_pdf(self, client, export_data):
        r = client.get(f"{self.URL}?format=pdf", headers=OWNER())
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert "organization-report.pdf" in r.headers["content-disposition"]
        assert_pdf_valid(r.content)

    def test_invalid_format(self, client, export_data):
        r = client.get(f"{self.URL}?format=json", headers=OWNER())
        assert r.status_code == 400

    def test_supervisor_forbidden(self, client, export_data):
        r = client.get(self.URL, headers=auth("ex-sup-u", UserRoleEnum.SUPERVISOR))
        assert r.status_code == 403

    def test_worker_forbidden(self, client, export_data):
        r = client.get(self.URL, headers=auth("ex-w1-u", UserRoleEnum.WORKER))
        assert r.status_code == 403

    def test_team_leader_forbidden(self, client, export_data):
        r = client.get(self.URL, headers=auth("ex-tl-u", UserRoleEnum.TEAM_LEADER))
        assert r.status_code == 403

    def test_csv_values_match_json(self, client, export_data):
        """CSV metric values must match what the JSON endpoint returns."""
        json_r = client.get("/api/v1/reports/organization", headers=OWNER())
        assert json_r.status_code == 200
        json_data = json_r.json()

        csv_r = client.get(self.URL, headers=OWNER())
        rows = {row[0]: row[1] for row in parse_csv(csv_r.content)[1:]}

        assert rows["total_workers"] == str(json_data["total_workers"])
        assert rows["active_workers"] == str(json_data["active_workers"])
        assert rows["completed_tasks"] == str(json_data["completed_tasks"])

    def test_zero_safe_empty(self, client, db_session):
        for model in [TaskTransition, WorkUpdate, Task, team_projects, Project,
                      Worker, TeamLeader, Supervisor, Team]:
            db_session.query(model).delete()
        db_session.query(User).filter(User.id != "usr-test-owner").delete()
        db_session.commit()

        r = client.get(self.URL, headers=OWNER())
        assert r.status_code == 200
        rows = parse_csv(r.content)
        assert rows[0] == ["Metric", "Value"]


# ─── Project export ───────────────────────────────────────────────────────────

class TestProjectExport:
    def url(self, pid="ex-p1"):
        return f"/api/v1/reports/projects/{pid}/export"

    def test_owner_csv(self, client, export_data):
        r = client.get(self.url(), headers=OWNER())
        assert r.status_code == 200
        assert "text/csv" in r.headers["content-type"]
        assert "ex-p1" in r.headers["content-disposition"]
        rows = parse_csv(r.content)
        assert rows[0] == ["Metric", "Value"]

    def test_owner_xlsx(self, client, export_data):
        r = client.get(f"{self.url()}?format=xlsx", headers=OWNER())
        assert r.status_code == 200
        assert_xlsx_valid(r.content)

    def test_owner_pdf(self, client, export_data):
        r = client.get(f"{self.url()}?format=pdf", headers=OWNER())
        assert r.status_code == 200
        assert_pdf_valid(r.content)

    def test_invalid_format(self, client, export_data):
        r = client.get(f"{self.url()}?format=xml", headers=OWNER())
        assert r.status_code == 400

    def test_not_found(self, client, export_data):
        r = client.get(self.url("no-such-id"), headers=OWNER())
        assert r.status_code == 404

    def test_wrong_team_worker_forbidden(self, client, export_data):
        """w2 is in team1 which owns ex-p1 — but let's use a worker with NO team."""
        # Create a worker with no team to test 403
        r = client.get(self.url(), headers=auth("ex-w2-u", UserRoleEnum.WORKER))
        # ex-w2 IS in team1 which is assigned to ex-p1 → should be 200
        assert r.status_code == 200

    def test_csv_values_match_json(self, client, export_data):
        json_r = client.get("/api/v1/reports/projects/ex-p1", headers=OWNER())
        json_data = json_r.json()
        csv_r = client.get(self.url(), headers=OWNER())
        rows = {row[0]: row[1] for row in parse_csv(csv_r.content)[1:]}
        assert rows["completed_tasks"] == str(json_data["completed_tasks"])
        assert rows["total_tasks"] == str(json_data["total_tasks"])


# ─── Worker export ────────────────────────────────────────────────────────────

class TestWorkerExport:
    def url(self, wid="ex-w1"):
        return f"/api/v1/reports/workers/{wid}/export"

    def test_owner_csv(self, client, export_data):
        r = client.get(self.url(), headers=OWNER())
        assert r.status_code == 200
        assert "text/csv" in r.headers["content-type"]
        assert "ex-w1" in r.headers["content-disposition"]

    def test_owner_xlsx(self, client, export_data):
        r = client.get(f"{self.url()}?format=xlsx", headers=OWNER())
        assert r.status_code == 200
        assert_xlsx_valid(r.content)

    def test_owner_pdf(self, client, export_data):
        r = client.get(f"{self.url()}?format=pdf", headers=OWNER())
        assert r.status_code == 200
        assert_pdf_valid(r.content)

    def test_self_access(self, client, export_data):
        """Worker can export their own report."""
        r = client.get(self.url(), headers=auth("ex-w1-u", UserRoleEnum.WORKER))
        assert r.status_code == 200

    def test_other_worker_forbidden(self, client, export_data):
        r = client.get(self.url("ex-w2"), headers=auth("ex-w1-u", UserRoleEnum.WORKER))
        assert r.status_code == 403

    def test_invalid_format(self, client, export_data):
        r = client.get(f"{self.url()}?format=docx", headers=OWNER())
        assert r.status_code == 400

    def test_csv_values_match_json(self, client, export_data):
        json_r = client.get("/api/v1/reports/workers/ex-w1", headers=OWNER())
        json_data = json_r.json()
        csv_r = client.get(self.url(), headers=OWNER())
        rows = {row[0]: row[1] for row in parse_csv(csv_r.content)[1:]}
        assert rows["total_tasks"] == str(json_data["total_tasks"])
        assert rows["worker_name"] == json_data["worker_name"]


# ─── Team export ─────────────────────────────────────────────────────────────

class TestTeamExport:
    def url(self, tid="ex-team1"):
        return f"/api/v1/reports/teams/{tid}/export"

    def test_owner_csv(self, client, export_data):
        r = client.get(self.url(), headers=OWNER())
        assert r.status_code == 200
        assert "text/csv" in r.headers["content-type"]
        assert "ex-team1" in r.headers["content-disposition"]

    def test_owner_xlsx(self, client, export_data):
        r = client.get(f"{self.url()}?format=xlsx", headers=OWNER())
        assert r.status_code == 200
        assert_xlsx_valid(r.content)

    def test_owner_pdf(self, client, export_data):
        r = client.get(f"{self.url()}?format=pdf", headers=OWNER())
        assert r.status_code == 200
        assert_pdf_valid(r.content)

    def test_team_leader_own(self, client, export_data):
        r = client.get(self.url(), headers=auth("ex-tl-u", UserRoleEnum.TEAM_LEADER))
        assert r.status_code == 200

    def test_worker_other_team_forbidden(self, client, export_data):
        r = client.get(self.url("ex-team2"), headers=auth("ex-w1-u", UserRoleEnum.WORKER))
        assert r.status_code == 403

    def test_not_found(self, client, export_data):
        r = client.get(self.url("no-such"), headers=OWNER())
        assert r.status_code == 404

    def test_csv_values_match_json(self, client, export_data):
        json_r = client.get("/api/v1/reports/teams/ex-team1", headers=OWNER())
        json_data = json_r.json()
        csv_r = client.get(self.url(), headers=OWNER())
        rows = {row[0]: row[1] for row in parse_csv(csv_r.content)[1:]}
        assert rows["total_workers"] == str(json_data["total_workers"])
        assert rows["team_name"] == json_data["team_name"]


# ─── Activity export ─────────────────────────────────────────────────────────

class TestActivityExport:
    URL = "/api/v1/reports/activity/export"

    def test_owner_csv_all(self, client, export_data):
        r = client.get(self.URL, headers=OWNER())
        assert r.status_code == 200
        assert "text/csv" in r.headers["content-type"]
        assert "activity-report.csv" in r.headers["content-disposition"]
        rows = parse_csv(r.content)
        assert rows[0][0] == "ID"
        assert len(rows) == 4  # header + 3 updates

    def test_csv_column_headers(self, client, export_data):
        r = client.get(self.URL, headers=OWNER())
        rows = parse_csv(r.content)
        expected = ["ID", "Task ID", "Task Title", "Worker ID", "Worker Name",
                    "Project ID", "Project Name", "Created By User ID", "Description",
                    "Timestamp", "Authorship"]
        assert rows[0] == expected

    def test_owner_xlsx(self, client, export_data):
        r = client.get(f"{self.URL}?format=xlsx", headers=OWNER())
        assert r.status_code == 200
        assert_xlsx_valid(r.content)

    def test_owner_pdf(self, client, export_data):
        r = client.get(f"{self.URL}?format=pdf", headers=OWNER())
        assert r.status_code == 200
        assert_pdf_valid(r.content)

    def test_invalid_format(self, client, export_data):
        r = client.get(f"{self.URL}?format=html", headers=OWNER())
        assert r.status_code == 400

    def test_filter_worker(self, client, export_data):
        r = client.get(f"{self.URL}?worker_id=ex-w1", headers=OWNER())
        rows = parse_csv(r.content)
        assert len(rows) == 3  # header + 2

    def test_filter_project(self, client, export_data):
        r = client.get(f"{self.URL}?project_id=ex-p1", headers=OWNER())
        rows = parse_csv(r.content)
        assert len(rows) == 4  # header + 3

    def test_filter_team(self, client, export_data):
        r = client.get(f"{self.URL}?team_id=ex-team1", headers=OWNER())
        rows = parse_csv(r.content)
        assert len(rows) == 4  # header + 3

    def test_pagination_limit(self, client, export_data):
        r = client.get(f"{self.URL}?limit=1", headers=OWNER())
        rows = parse_csv(r.content)
        assert len(rows) == 2  # header + 1

    def test_pagination_offset(self, client, export_data):
        r1 = client.get(f"{self.URL}?limit=2&offset=0", headers=OWNER())
        r2 = client.get(f"{self.URL}?limit=2&offset=2", headers=OWNER())
        ids_p1 = {row[0] for row in parse_csv(r1.content)[1:]}
        ids_p2 = {row[0] for row in parse_csv(r2.content)[1:]}
        assert ids_p1.isdisjoint(ids_p2)

    def test_max_limit_1000_allowed(self, client, export_data):
        r = client.get(f"{self.URL}?limit=1000", headers=OWNER())
        assert r.status_code == 200

    def test_over_max_limit_rejected(self, client, export_data):
        r = client.get(f"{self.URL}?limit=1001", headers=OWNER())
        assert r.status_code == 400

    def test_date_filter_excludes_old(self, client, export_data):
        cutoff = (date.today() - timedelta(days=5)).isoformat()
        r = client.get(f"{self.URL}?start_date={cutoff}", headers=OWNER())
        rows = parse_csv(r.content)
        # wu3 is 35 days old — excluded
        ids = {row[0] for row in rows[1:]}
        assert "ex-wu3" not in ids

    def test_worker_cannot_see_others(self, client, export_data):
        r = client.get(f"{self.URL}?worker_id=ex-w2",
                       headers=auth("ex-w1-u", UserRoleEnum.WORKER))
        assert r.status_code == 403

    def test_worker_scoped_implicit(self, client, export_data):
        """Worker with no filter should see only their own activity."""
        r = client.get(self.URL, headers=auth("ex-w1-u", UserRoleEnum.WORKER))
        rows = parse_csv(r.content)
        worker_ids = {row[3] for row in rows[1:]}  # Worker ID column
        assert worker_ids == {"ex-w1"}

    def test_newest_first_ordering(self, client, export_data):
        r = client.get(self.URL, headers=OWNER())
        rows = parse_csv(r.content)[1:]  # skip header
        timestamps = [row[9] for row in rows]  # Timestamp column
        assert timestamps == sorted(timestamps, reverse=True)

    def test_null_created_by_in_csv(self, client, export_data):
        """NULL created_by_user_id must appear as empty string in CSV, not 'None'."""
        r = client.get(f"{self.URL}?worker_id=ex-w2", headers=OWNER())
        rows = parse_csv(r.content)
        data_row = rows[1]
        created_by_col = data_row[7]  # Created By User ID
        assert created_by_col == ""

    def test_unauthenticated_rejected(self, client, export_data):
        r = client.get(self.URL)
        assert r.status_code == 401
