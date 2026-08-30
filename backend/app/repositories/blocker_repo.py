from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.blocker import Blocker, BlockerStatusEnum
from app.repositories.base import BaseRepository


class BlockerRepository(BaseRepository[Blocker]):
    def __init__(self, db: Session):
        super().__init__(Blocker, db)

    def get_by_project(self, project_id: str) -> List[Blocker]:
        return self.db.query(Blocker).filter(Blocker.project_id == project_id).all()

    def get_open_blockers(self) -> List[Blocker]:
        return self.db.query(Blocker).filter(Blocker.status == BlockerStatusEnum.OPEN).all()
