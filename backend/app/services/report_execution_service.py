import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import EntityNotFoundException
from app.models.project import Project
from app.models.report_run import ReportRun
from app.models.report_schedule import ReportSchedule, ReportTypeEnum
from app.models.team import Team
from app.models.user import Worker
from app.services.report_export_service import ReportExportService
from app.services.report_run_service import ReportRunService
from app.services.report_scheduling_utils import calculate_next_run_at
from app.services.report_service import ReportService
from app.services.report_storage_service import ReportStorageService

logger = logging.getLogger(__name__)


class ReportExecutionService:
    def __init__(self, db: Session):
        self.db = db

    def execute_scheduled(self, schedule: ReportSchedule) -> ReportRun:
        now_utc = datetime.now(timezone.utc)

        if not schedule.is_active:
            raise ValueError("Cannot execute inactive schedule")

        next_run_at = schedule.next_run_at
        if next_run_at.tzinfo is None:
            next_run_at = next_run_at.replace(tzinfo=timezone.utc)

        if next_run_at > now_utc:
            raise ValueError("Schedule is not yet due")

        scheduled_for = next_run_at

        # Transaction 1: Claim
        run = ReportRunService.create_scheduled_run(self.db, schedule.id, scheduled_for)

        schedule.next_run_at = calculate_next_run_at(
            scheduled_for, schedule.frequency, now_utc
        )
        schedule.last_run_at = scheduled_for
        self.db.commit()

        return self._execute_run(run, schedule)

    def execute_manual(self, schedule: ReportSchedule) -> ReportRun:
        if not schedule.is_active:
            raise ValueError("Cannot execute inactive schedule")

        run = ReportRunService.create_manual_run(self.db, schedule.id)
        self.db.commit()

        return self._execute_run(run, schedule)

    def _execute_run(self, run: ReportRun, schedule: ReportSchedule) -> ReportRun:
        ReportRunService.mark_running(self.db, run.id)
        self.db.commit()

        try:
            report_data = self._generate_report(schedule)

            # Export bytes
            exporter = ReportExportService()
            rt = schedule.report_type
            if rt == ReportTypeEnum.ORGANIZATION:
                content, _, _ = exporter.export_organization(
                    report_data, schedule.export_format.value
                )
            elif rt == ReportTypeEnum.PROJECT:
                content, _, _ = exporter.export_project(
                    report_data, schedule.export_format.value
                )
            elif rt == ReportTypeEnum.WORKER:
                content, _, _ = exporter.export_worker(
                    report_data, schedule.export_format.value
                )
            elif rt == ReportTypeEnum.TEAM:
                content, _, _ = exporter.export_team(
                    report_data, schedule.export_format.value
                )
            elif rt == ReportTypeEnum.ACTIVITY:
                content, _, _ = exporter.export_activity(
                    report_data, schedule.export_format.value
                )
            else:
                raise ValueError(f"Unknown report type: {rt}")

            storage = ReportStorageService(settings.REPORT_STORAGE_PATH)
            path, filename = storage.write(
                content,
                schedule.report_type.value,
                schedule.id,
                run.scheduled_for,
                schedule.export_format.value,
            )

            ReportRunService.mark_completed(self.db, run.id, str(path), filename)
            self.db.commit()

        except Exception as exc:
            logger.exception("Report execution failed for run %s", run.id)
            error_msg = str(exc)[:500] if str(exc) else "An unexpected error occurred"
            ReportRunService.mark_failed(self.db, run.id, error_msg)
            self.db.commit()

        return run

    def _generate_report(self, schedule: ReportSchedule):
        svc = ReportService(self.db)
        rt = schedule.report_type
        sid = schedule.scope_id

        if rt == ReportTypeEnum.ORGANIZATION:
            return svc.get_organization_report()

        elif rt == ReportTypeEnum.PROJECT:
            if not sid:
                raise ValueError("Scope ID required for project report")
            project = self.db.query(Project).filter(Project.id == sid).first()
            if not project:
                raise EntityNotFoundException(entity_name="Project", entity_id=sid)
            return svc.get_project_report(project)

        elif rt == ReportTypeEnum.WORKER:
            if not sid:
                raise ValueError("Scope ID required for worker report")
            worker = self.db.query(Worker).filter(Worker.id == sid).first()
            if not worker:
                raise EntityNotFoundException(entity_name="Worker", entity_id=sid)
            return svc.get_worker_report(worker)

        elif rt == ReportTypeEnum.TEAM:
            if not sid:
                raise ValueError("Scope ID required for team report")
            team = self.db.query(Team).filter(Team.id == sid).first()
            if not team:
                raise EntityNotFoundException(entity_name="Team", entity_id=sid)
            return svc.get_team_report(team)

        elif rt == ReportTypeEnum.ACTIVITY:
            return svc.get_activity_report(
                start_date=None,
                end_date=None,
                project_id=None,
                team_id=None,
                worker_id=None,
                limit=1000,
            )
        else:
            raise ValueError(f"Unknown report type: {rt}")
