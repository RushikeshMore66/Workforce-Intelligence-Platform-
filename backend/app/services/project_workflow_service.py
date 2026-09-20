from typing import Dict, Set

from app.core.exceptions import PermissionDeniedException
from app.models.project import Project, ProjectStatusEnum
from app.models.user import User, UserRoleEnum


class ProjectWorkflowService:
    """Validates project lifecycle transitions."""

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
