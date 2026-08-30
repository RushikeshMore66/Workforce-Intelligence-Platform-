from typing import List
from sqlalchemy.orm import Session
from app.models.user import Supervisor
from app.repositories.supervisor_repo import SupervisorRepository
from app.core.exceptions import EntityNotFoundException


class SupervisorService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SupervisorRepository(db)

    def get_supervisors(self) -> List[Supervisor]:
        return self.repo.get_all()

    def get_supervisor(self, supervisor_id: str) -> Supervisor:
        sup = self.repo.get_by_id(supervisor_id)
        if not sup:
            raise EntityNotFoundException("Supervisor", supervisor_id)
        return sup
