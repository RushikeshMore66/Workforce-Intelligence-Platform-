from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.task import Task, TaskStatusEnum
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: Session):
        super().__init__(Task, db)

    def get_by_project(self, project_id: str) -> List[Task]:
        return self.db.query(Task).filter(Task.project_id == project_id).order_by(Task.due_date.asc()).all()

    def get_by_worker(self, worker_id: str) -> List[Task]:
        return self.db.query(Task).filter(Task.assignee_id == worker_id).order_by(Task.due_date.asc()).all()

    def get_by_team(self, team_id: str) -> List[Task]:
        return self.db.query(Task).filter(Task.team_id == team_id).all()

    def get_by_status(self, status: TaskStatusEnum) -> List[Task]:
        return self.db.query(Task).filter(Task.status == status).all()
