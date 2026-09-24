"""User-level audit log.

Captures account lifecycle events (create, activate, deactivate, password
change, profile update) that are not project-scoped.  This table is separate
from ProjectActivity which requires a project_id FK.

Events are immutable records; there is no update or delete operation.
"""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class UserAuditEventEnum(str, enum.Enum):
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_ACTIVATED = "USER_ACTIVATED"
    USER_DEACTIVATED = "USER_DEACTIVATED"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"


class UserAuditLog(Base):
    """Immutable per-user lifecycle event record."""

    __tablename__ = "user_audit_logs"

    id = Column(String, primary_key=True, index=True)

    # The user whose account was acted upon
    target_user_id = Column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # The user who performed the action (may be NULL for system actions)
    actor_user_id = Column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Snapshot of actor name at event time (survives user deletion)
    actor_name = Column(String, nullable=False)

    event = Column(
        Enum(UserAuditEventEnum, name="user_audit_event_enum"),
        nullable=False,
        index=True,
    )

    # Optional human-readable description or diff
    description = Column(Text, nullable=True)

    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    # Relationships (read-only; audit log must never be mutated)
    target_user = relationship(
        "User",
        foreign_keys=[target_user_id],
        # Do not back_populate onto User to keep User model clean
    )
    actor_user = relationship(
        "User",
        foreign_keys=[actor_user_id],
    )
