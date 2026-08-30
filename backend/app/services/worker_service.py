from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import Worker, WorkerStatusEnum
from app.repositories.worker_repo import WorkerRepository
from app.core.exceptions import EntityNotFoundException


class WorkerService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = WorkerRepository(db)

    def get_workers(
        self,
        search: Optional[str] = None,
        team_id: Optional[str] = None,
        status: Optional[WorkerStatusEnum] = None,
    ) -> List[Worker]:
        return self.repo.filter_workers(search=search, team_id=team_id, status=status)

    def get_worker(self, worker_id: str) -> Worker:
        worker = self.repo.get_by_id(worker_id)
        if not worker:
            raise EntityNotFoundException("Worker", worker_id)
        return worker
