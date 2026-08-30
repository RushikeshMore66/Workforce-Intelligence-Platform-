from typing import List
from sqlalchemy.orm import Session
from app.models.team import Team
from app.repositories.team_repo import TeamRepository
from app.core.exceptions import EntityNotFoundException


class TeamService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TeamRepository(db)

    def get_teams(self) -> List[Team]:
        return self.repo.get_all()

    def get_team(self, team_id: str) -> Team:
        team = self.repo.get_by_id(team_id)
        if not team:
            raise EntityNotFoundException("Team", team_id)
        return team
