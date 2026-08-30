from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.project import Project, ProjectStatusEnum, ProjectHealthEnum, ProjectPriorityEnum
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)

    def filter_projects(
        self,
        search: Optional[str] = None,
        status: Optional[ProjectStatusEnum] = None,
        health: Optional[ProjectHealthEnum] = None,
        priority: Optional[ProjectPriorityEnum] = None,
        supervisor_id: Optional[str] = None,
    ) -> List[Project]:
        query = self.db.query(Project)
        if search:
            query = query.filter(
                (Project.name.ilike(f"%{search}%")) | (Project.client.ilike(f"%{search}%"))
            )
        if status:
            query = query.filter(Project.status == status)
        if health:
            query = query.filter(Project.health == health)
        if priority:
            query = query.filter(Project.priority == priority)
        if supervisor_id:
            query = query.filter(Project.supervisor_id == supervisor_id)
        return query.order_by(Project.deadline.asc()).all()

    def get_by_supervisor(self, supervisor_id: str) -> List[Project]:
        return self.db.query(Project).filter(Project.supervisor_id == supervisor_id).all()
