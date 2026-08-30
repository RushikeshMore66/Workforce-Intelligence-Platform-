from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: Session):
        super().__init__(Notification, db)

    def get_user_notifications(self, user_id: Optional[str] = None) -> List[Notification]:
        query = self.db.query(Notification)
        if user_id:
            query = query.filter((Notification.user_id == user_id) | (Notification.user_id.is_(None)))
        return query.order_by(Notification.timestamp.desc()).all()

    def mark_all_read(self, user_id: Optional[str] = None) -> int:
        query = self.db.query(Notification).filter(Notification.read == False)
        if user_id:
            query = query.filter((Notification.user_id == user_id) | (Notification.user_id.is_(None)))
        count = query.update({Notification.read: True}, synchronize_session=False)
        self.db.commit()
        return count
