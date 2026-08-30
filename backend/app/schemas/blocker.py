from datetime import date
from typing import Optional
from app.schemas.common import BaseSchema, BlockerStatus


class BlockerBase(BaseSchema):
    project_id: str
    task_id: Optional[str] = None
    title: str
    description: str
    team_id: Optional[str] = None


class BlockerCreate(BlockerBase):
    pass


class BlockerUpdate(BaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[BlockerStatus] = None
    resolved_date: Optional[date] = None


class BlockerOut(BlockerBase):
    id: str
    reported_by_id: Optional[str] = None
    created_date: date
    resolved_date: Optional[date] = None
    status: BlockerStatus
