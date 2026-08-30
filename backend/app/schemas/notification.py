from datetime import datetime
from typing import Optional
from app.schemas.common import BaseSchema, NotificationType
from app.models.notification import NotificationPriorityEnum


class NotificationCreate(BaseSchema):
    type: NotificationType
    title: str
    description: str
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    priority: NotificationPriorityEnum = NotificationPriorityEnum.MEDIUM


class NotificationUpdate(BaseSchema):
    read: Optional[bool] = None


class NotificationOut(BaseSchema):
    id: str
    type: NotificationType
    title: str
    description: str
    project_id: Optional[str] = None
    read: bool
    timestamp: datetime
    priority: NotificationPriorityEnum
