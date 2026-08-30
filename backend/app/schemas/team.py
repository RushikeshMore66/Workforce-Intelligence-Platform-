from typing import Optional, List
from app.schemas.common import BaseSchema


class TeamBase(BaseSchema):
    name: str
    supervisor_id: Optional[str] = None
    team_leader_id: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseSchema):
    name: Optional[str] = None
    supervisor_id: Optional[str] = None
    team_leader_id: Optional[str] = None


class TeamOut(TeamBase):
    id: str
    member_count: int = 0
    project_ids: List[str] = []
