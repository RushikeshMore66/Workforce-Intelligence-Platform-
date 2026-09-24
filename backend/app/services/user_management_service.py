"""User Management Service.

This service owns the complete user lifecycle:
  - create_user:      atomically creates User + role profile + audit event
  - update_user:      updates allowed fields, writes audit event
  - deactivate_user:  sets is_active=False, writes audit event
  - activate_user:    sets is_active=True, writes audit event
  - change_password:  verifies current password, hashes and stores new one

All mutations commit atomically.  On any validation failure the transaction is
rolled back so no partial state is persisted.

Organizational integrity rules:
  - WORKER: if team_leader_id is provided, that team leader must belong to the
    same team as the worker.
  - WORKER: if supervisor_id is provided, that supervisor must own the team (if
    team_id is also provided).
  - TEAM_LEADER: team_id must reference an existing Team.
  - OWNER role cannot be created through this service endpoint.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
    BusinessRuleException,
    DuplicateEntityException,
    EntityNotFoundException,
    PermissionDeniedException,
)
from app.core.security import get_password_hash, verify_password
from app.models.team import Team
from app.models.user import Supervisor, TeamLeader, User, UserRoleEnum, Worker
from app.models.user_audit import UserAuditEventEnum, UserAuditLog
from app.schemas.user import UserCreate, UserUpdate


def _generate_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _generate_initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name.strip()[:2].upper()


def _write_audit(
    db: Session,
    event: UserAuditEventEnum,
    target_user: User,
    actor: User,
    description: str,
) -> None:
    log = UserAuditLog(
        id=_generate_id("ual"),
        event=event,
        target_user_id=target_user.id,
        actor_user_id=actor.id,
        actor_name=actor.name,
        description=description,
        timestamp=datetime.utcnow(),
    )
    db.add(log)


class UserManagementService:
    def __init__(self, db: Session):
        self.db = db

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _get_user_or_404(self, user_id: str) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise EntityNotFoundException("User", user_id)
        return user

    def _check_email_unique(self, email: str, exclude_id: Optional[str] = None) -> None:
        q = self.db.query(User).filter(User.email == email)
        if exclude_id:
            q = q.filter(User.id != exclude_id)
        if q.first():
            raise DuplicateEntityException(f"A user with email '{email}' already exists.")

    def _validate_team_exists(self, team_id: str) -> Team:
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise BusinessRuleException(f"Team '{team_id}' does not exist.")
        return team

    def _validate_team_leader_belongs_to_team(
        self, team_leader_id: str, team_id: str
    ) -> TeamLeader:
        leader = (
            self.db.query(TeamLeader)
            .filter(TeamLeader.id == team_leader_id)
            .first()
        )
        if not leader:
            raise BusinessRuleException(
                f"TeamLeader profile '{team_leader_id}' does not exist."
            )
        if leader.team_id != team_id:
            raise BusinessRuleException(
                f"TeamLeader '{team_leader_id}' does not lead team '{team_id}'. "
                "A worker's team leader must lead the same team."
            )
        return leader

    def _validate_supervisor_exists(self, supervisor_id: str) -> Supervisor:
        sup = (
            self.db.query(Supervisor)
            .filter(Supervisor.id == supervisor_id)
            .first()
        )
        if not sup:
            raise BusinessRuleException(
                f"Supervisor profile '{supervisor_id}' does not exist."
            )
        return sup

    def _validate_supervisor_owns_team(
        self, supervisor: Supervisor, team_id: str
    ) -> None:
        team = self._validate_team_exists(team_id)
        if team.supervisor_id != supervisor.id:
            raise BusinessRuleException(
                f"Supervisor '{supervisor.id}' does not manage team '{team_id}'. "
                "A worker's supervisor must manage the assigned team."
            )

    # ── Public operations ──────────────────────────────────────────────────────

    def create_user(self, data: UserCreate, actor: User) -> User:
        """Create a new User and its role profile atomically.

        Raises:
            PermissionDeniedException: if role is OWNER (owners cannot be
                provisioned through this endpoint).
            DuplicateEntityException: if email already exists.
            BusinessRuleException: if organizational relationships are invalid.
        """
        if data.role == UserRoleEnum.OWNER:
            raise PermissionDeniedException(
                "OWNER accounts cannot be created through the user management API."
            )

        self._check_email_unique(data.email)

        user_id = _generate_id("usr")
        initials = (
            data.avatar_initials.strip()
            if data.avatar_initials
            else _generate_initials(data.name)
        )

        user = User(
            id=user_id,
            email=data.email,
            name=data.name,
            hashed_password=get_password_hash(data.password),
            role=data.role,
            company=data.company,
            avatar_initials=initials,
            is_active=True,
        )
        self.db.add(user)
        self.db.flush()  # get user.id, but don't commit yet

        # Create role-specific profile
        if data.role == UserRoleEnum.SUPERVISOR:
            sup = Supervisor(
                id=_generate_id("sup"),
                user_id=user.id,
            )
            self.db.add(sup)

        elif data.role == UserRoleEnum.TEAM_LEADER:
            team_id = None
            if data.team_leader_profile and data.team_leader_profile.team_id:
                self._validate_team_exists(data.team_leader_profile.team_id)
                team_id = data.team_leader_profile.team_id
            leader = TeamLeader(
                id=_generate_id("tl"),
                user_id=user.id,
                team_id=team_id,
            )
            self.db.add(leader)

        elif data.role == UserRoleEnum.WORKER:
            if not data.worker_profile:
                raise BusinessRuleException(
                    "worker_profile is required when creating a WORKER account."
                )
            wp = data.worker_profile
            team_id = wp.team_id
            team_leader_id = wp.team_leader_id
            supervisor_id = wp.supervisor_id

            # Validate team
            if team_id:
                self._validate_team_exists(team_id)

            # Validate team leader belongs to same team
            if team_leader_id and team_id:
                self._validate_team_leader_belongs_to_team(team_leader_id, team_id)
            elif team_leader_id and not team_id:
                raise BusinessRuleException(
                    "team_id must be provided when team_leader_id is specified."
                )

            # Validate supervisor exists
            sup_obj = None
            if supervisor_id:
                sup_obj = self._validate_supervisor_exists(supervisor_id)
                # If team is also provided, supervisor must own it
                if team_id:
                    self._validate_supervisor_owns_team(sup_obj, team_id)

            worker = Worker(
                id=_generate_id("wrk"),
                user_id=user.id,
                role=wp.job_title,
                team_id=team_id,
                team_leader_id=team_leader_id,
                supervisor_id=supervisor_id,
                status=wp.status,
            )
            self.db.add(worker)

        # Write audit event
        _write_audit(
            self.db,
            UserAuditEventEnum.USER_CREATED,
            user,
            actor,
            f"User '{user.name}' ({user.role.value}) created by '{actor.name}'",
        )

        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: str, data: UserUpdate, actor: User) -> User:
        """Update allowed profile fields.  Role changes are owner-only."""
        user = self._get_user_or_404(user_id)

        changed_fields = []

        if data.name is not None and data.name != user.name:
            user.name = data.name
            changed_fields.append("name")

        if data.company is not None and data.company != user.company:
            user.company = data.company
            changed_fields.append("company")

        if data.avatar_initials is not None and data.avatar_initials != user.avatar_initials:
            user.avatar_initials = data.avatar_initials
            changed_fields.append("avatar_initials")

        if data.role is not None and data.role != user.role:
            # Only owners can change roles
            if actor.role != UserRoleEnum.OWNER:
                raise PermissionDeniedException("Only owners can change a user's role.")
            user.role = data.role
            changed_fields.append("role")

        if changed_fields:
            user.updated_at = datetime.utcnow()
            _write_audit(
                self.db,
                UserAuditEventEnum.USER_UPDATED,
                user,
                actor,
                f"Fields updated: {', '.join(changed_fields)}",
            )
            self.db.commit()
            self.db.refresh(user)

        return user

    def activate_user(self, user_id: str, actor: User) -> User:
        """Set is_active=True.  No-op if already active."""
        user = self._get_user_or_404(user_id)
        if not user.is_active:
            user.is_active = True
            user.updated_at = datetime.utcnow()
            _write_audit(
                self.db,
                UserAuditEventEnum.USER_ACTIVATED,
                user,
                actor,
                f"Account activated by '{actor.name}'",
            )
            self.db.commit()
            self.db.refresh(user)
        return user

    def deactivate_user(self, user_id: str, actor: User) -> User:
        """Set is_active=False.  Cannot deactivate yourself."""
        user = self._get_user_or_404(user_id)
        if user.id == actor.id:
            raise BusinessRuleException("You cannot deactivate your own account.")
        if user.is_active:
            user.is_active = False
            user.updated_at = datetime.utcnow()
            _write_audit(
                self.db,
                UserAuditEventEnum.USER_DEACTIVATED,
                user,
                actor,
                f"Account deactivated by '{actor.name}'",
            )
            self.db.commit()
            self.db.refresh(user)
        return user

    def update_own_profile(
        self,
        user: User,
        name: Optional[str],
        company: Optional[str],
        avatar_initials: Optional[str],
    ) -> User:
        """Authenticated user updates their own safe profile fields.

        Role and is_active cannot be changed through this method.
        """
        changed = []
        if name is not None and name != user.name:
            user.name = name
            changed.append("name")
        if company is not None and company != user.company:
            user.company = company
            changed.append("company")
        if avatar_initials is not None and avatar_initials != user.avatar_initials:
            user.avatar_initials = avatar_initials
            changed.append("avatar_initials")

        if changed:
            user.updated_at = datetime.utcnow()
            _write_audit(
                self.db,
                UserAuditEventEnum.USER_UPDATED,
                user,
                user,  # actor == target for self-updates
                f"Self-updated profile fields: {', '.join(changed)}",
            )
            self.db.commit()
            self.db.refresh(user)

        return user

    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:
        """Verify current_password and store hash of new_password.

        Raises:
            BusinessRuleException: if current_password does not match.
        """
        if not verify_password(current_password, user.hashed_password):
            raise BusinessRuleException("Current password is incorrect.")

        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()

        _write_audit(
            self.db,
            UserAuditEventEnum.PASSWORD_CHANGED,
            user,
            user,
            "Password changed by account holder",
        )
        self.db.commit()

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Return all users.  Only callable by OWNER (enforced at router layer)."""
        return (
            self.db.query(User)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user(self, user_id: str) -> User:
        return self._get_user_or_404(user_id)
