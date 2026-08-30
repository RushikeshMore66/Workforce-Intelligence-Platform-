from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import Supervisor
from app.repositories.base import BaseRepository


class SupervisorRepository(BaseRepository[Supervisor]):
    def __init__(self, db: Session):
        super().__init__(Supervisor, db)
