from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.team import Team
from app.repositories.base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    def __init__(self, db: Session):
        super().__init__(Team, db)

    def get_by_supervisor(self, supervisor_id: str) -> List[Team]:
        return self.db.query(Team).filter(Team.supervisor_id == supervisor_id).all()
