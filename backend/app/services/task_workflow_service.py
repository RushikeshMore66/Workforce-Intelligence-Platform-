import uuid
from typing import Dict, Set

from sqlalchemy.orm import Session

from app.authorization.policies import authorize_task_access
from app.core.exceptions import EntityNotFoundException, PermissionDeniedException
from app.models.task import Task, TaskStatusEnum, TaskTransition
from app.models.user import User, UserRoleEnum


class TaskWorkflowService:
    """Single source of truth for task status transitions."""

    ALLOWED_TRANSITIONS: Dict[TaskStatusEnum, Set[TaskStatusEnum]] = {
        TaskStatusEnum.PLANNED: {
            TaskStatusEnum.IN_PROGRESS,
            TaskStatusEnum.CANCELLED,
        },
        TaskStatusEnum.IN_PROGRESS: {
            TaskStatusEnum.ON_HOLD,
            TaskStatusEnum.COMPLETED,
            TaskStatusEnum.CANCELLED,
        },
        TaskStatusEnum.ON_HOLD: {
            TaskStatusEnum.IN_PROGRESS,
            TaskStatusEnum.CANCELLED,
        },
        TaskStatusEnum.COMPLETED: set(),
        TaskStatusEnum.CANCELLED: set(),
    }

    def __init__(self, db: Session):
        self.db = db

    def transition(
        self,
        task_id: str,
        to_status: TaskStatusEnum,
        current_user: User,
        reason: str | None = None,
    ) -> Task:
        task = (
            self.db.query(Task)
            .with_for_update()
            .filter(Task.id == task_id)
            .first()
        )

        if not task:
            raise EntityNotFoundException("Task", task_id)

        authorize_task_access(task_id, current_user, self.db)

        if task.status == to_status:
            raise PermissionDeniedException(
                "The task is already in the requested status."
            )

        allowed_targets = self.ALLOWED_TRANSITIONS.get(task.status, set())
        if to_status not in allowed_targets:
            raise PermissionDeniedException(
                f"Invalid task transition: "
                f"{task.status.value} -> {to_status.value}."
            )

        if (
            to_status == TaskStatusEnum.CANCELLED
            and current_user.role == UserRoleEnum.WORKER
        ):
            raise PermissionDeniedException(
                "Workers cannot cancel tasks. Ask your supervisor or team leader."
            )

        if to_status == TaskStatusEnum.ON_HOLD and not (reason and reason.strip()):
            raise PermissionDeniedException(
                "A reason is required when putting a task on hold."
            )

        old_status = task.status
        task.status = to_status

        transition = TaskTransition(
            id=f"tt-{uuid.uuid4().hex[:10]}",
            task_id=task.id,
            from_status=old_status,
            to_status=to_status,
            changed_by_user_id=current_user.id,
            reason=reason.strip() if reason else None,
        )

        self.db.add(transition)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task
