from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.user import Worker, User, WorkerStatusEnum
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
        # Always join User so _format_worker can access w.user without N+1 queries
        query = self.db.query(Worker).join(Worker.user).options(joinedload(Worker.user))

        if search:
            # Search by worker role title OR user name
            query = query.filter(
                Worker.role.ilike(f"%{search}%") | User.name.ilike(f"%{search}%")
            )
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
