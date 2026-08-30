from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.notification import NotificationOut
from app.repositories.notification_repo import NotificationRepository
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationOut])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = NotificationRepository(db)
    return repo.get_user_notifications(current_user.id)


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_as_read(
    notification_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    repo = NotificationRepository(db)
    notif = repo.get_by_id(notification_id)
    if not notif:
        raise EntityNotFoundException("Notification", notification_id)
    return repo.update(notif, {"read": True})


@router.post("/read-all", response_model=dict)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = NotificationRepository(db)
    updated_count = repo.mark_all_read(current_user.id)
    return {"message": f"Marked {updated_count} notifications as read", "count": updated_count}
