from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import Worker, WorkerStatusEnum
from app.repositories.base import BaseRepository


class WorkerRepository(BaseRepository[Worker]):
    def __init__(self, db: Session):
        super().__init__(Worker, db)

    def filter_workers(
        self,
        search: Optional[str] = None,
        team_id: Optional[str] = None,
        status: Optional[WorkerStatusEnum] = None,
        supervisor_id: Optional[str] = None,
    ) -> List[Worker]:
        query = self.db.query(Worker)
        if search:
            query = query.filter(Worker.role.ilike(f"%{search}%"))
        if team_id:
            query = query.filter(Worker.team_id == team_id)
        if status:
            query = query.filter(Worker.status == status)
        if supervisor_id:
            query = query.filter(Worker.supervisor_id == supervisor_id)
        return query.all()

    def get_by_team(self, team_id: str) -> List[Worker]:
        return self.db.query(Worker).filter(Worker.team_id == team_id).all()

    def get_by_supervisor(self, supervisor_id: str) -> List[Worker]:
        return self.db.query(Worker).filter(Worker.supervisor_id == supervisor_id).all()
