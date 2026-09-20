from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException
from app.models.project import Project
from app.models.task import Task, TaskStatusEnum


class ProjectProgressService:
    """Maintains project progress as a derived value from task execution."""

    @staticmethod
    def recalculate_project_progress(
        db: Session,
        project_id: str,
    ) -> Project:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise EntityNotFoundException("Project", project_id)

        active_task_count = (
            db.query(func.count(Task.id))
            .filter(
                Task.project_id == project_id,
                Task.status != TaskStatusEnum.CANCELLED,
            )
            .scalar()
            or 0
        )

        completed_task_count = (
            db.query(func.count(Task.id))
            .filter(
                Task.project_id == project_id,
                Task.status == TaskStatusEnum.COMPLETED,
            )
            .scalar()
            or 0
        )

        if active_task_count == 0:
            progress = 0
        else:
            progress = round((completed_task_count / active_task_count) * 100)

        project.progress = max(0, min(100, progress))
        db.add(project)
        db.flush()

        return project
