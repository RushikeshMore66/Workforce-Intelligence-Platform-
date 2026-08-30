from datetime import datetime
from typing import Optional
from app.schemas.common import BaseSchema
from app.models.activity import ActivityTypeEnum


class ActivityCreate(BaseSchema):
    project_id: str
    description: str
    user_id: Optional[str] = None
    user_name: str
    type: ActivityTypeEnum


class ActivityOut(BaseSchema):
    id: str
    project_id: str
    description: str
    user_id: Optional[str] = None
    user_name: str
    timestamp: datetime
    type: ActivityTypeEnum
