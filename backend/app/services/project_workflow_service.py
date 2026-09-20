from typing import Dict, Set

from sqlalchemy.orm import Session

from app.core.exceptions import PermissionDeniedException
from app.models.project import Project, ProjectStatusEnum
from app.models.task import Task, TaskStatusEnum
from app.models.user import User, UserRoleEnum


class ProjectWorkflowService:
    """Validates project lifecycle transitions against actual task execution."""

    ALLOWED_TRANSITIONS: Dict[ProjectStatusEnum, Set[ProjectStatusEnum]] = {
        ProjectStatusEnum.PLANNED: {
            ProjectStatusEnum.ACTIVE,
            ProjectStatusEnum.CANCELLED,
        },
        ProjectStatusEnum.ACTIVE: {
            ProjectStatusEnum.ON_HOLD,
            ProjectStatusEnum.COMPLETED,
            ProjectStatusEnum.CANCELLED,
        },
        ProjectStatusEnum.ON_HOLD: {
            ProjectStatusEnum.ACTIVE,
            ProjectStatusEnum.CANCELLED,
        },
        ProjectStatusEnum.COMPLETED: set(),
        ProjectStatusEnum.CANCELLED: set(),
    }

    @classmethod
    def validate_transition(
        cls,
        project: Project,
        to_status: ProjectStatusEnum,
        user: User,
        db: Session,
        reason: str | None = None,
    ) -> None:
        if user.role not in {
            UserRoleEnum.OWNER,
            UserRoleEnum.SUPERVISOR,
        }:
            raise PermissionDeniedException(
                "Only owners and supervisors can change project lifecycle status."
            )

        if (
            to_status == ProjectStatusEnum.CANCELLED
            and user.role != UserRoleEnum.OWNER
        ):
            raise PermissionDeniedException(
                "Only the owner can cancel a project."
            )

        if to_status in {
            ProjectStatusEnum.ON_HOLD,
            ProjectStatusEnum.CANCELLED,
        } and not (reason and reason.strip()):
            raise PermissionDeniedException(
                "A reason is required when putting a project on hold or cancelling it."
            )

        if project.status == to_status:
            raise PermissionDeniedException(
                "The project is already in the requested status."
            )

        allowed = cls.ALLOWED_TRANSITIONS.get(project.status, set())
        if to_status not in allowed:
            raise PermissionDeniedException(
                f"Invalid project transition: "
                f"{project.status.value} -> {to_status.value}."
            )

        if to_status != ProjectStatusEnum.COMPLETED:
            return

        tasks = (
            db.query(Task)
            .filter(Task.project_id == project.id)
            .all()
        )

        non_cancelled_tasks = [
            task for task in tasks
            if task.status != TaskStatusEnum.CANCELLED
        ]

        if not non_cancelled_tasks:
            raise PermissionDeniedException(
                "A project cannot be completed without at least one completed task."
            )

        incomplete_tasks = [
            task for task in non_cancelled_tasks
            if task.status != TaskStatusEnum.COMPLETED
        ]

        if incomplete_tasks:
            raise PermissionDeniedException(
                "A project cannot be completed while any active task is not completed."
            )
