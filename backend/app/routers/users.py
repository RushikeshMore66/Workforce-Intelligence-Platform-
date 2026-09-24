"""User management API — Owner only.

GET  /api/v1/users            — list all users
GET  /api/v1/users/{id}       — get a specific user
POST /api/v1/users            — create a new user with role profile
PATCH /api/v1/users/{id}      — update allowed user fields
POST /api/v1/users/{id}/activate   — activate a deactivated user
POST /api/v1/users/{id}/deactivate — deactivate an active user

All endpoints require authentication and OWNER role.
The backend enforces this — frontend role-hiding is supplementary only.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.exceptions import PermissionDeniedException
from app.database import get_db
from app.models.user import User, UserRoleEnum
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.services.user_management_service import UserManagementService

router = APIRouter(prefix="/users", tags=["Users"])


def _require_owner(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that ensures the caller is an OWNER."""
    if current_user.role != UserRoleEnum.OWNER:
        raise PermissionDeniedException(
            "Only users with OWNER role can manage user accounts."
        )
    return current_user


def _build_user_out(user: User) -> UserOut:
    """Map a User ORM object to the safe UserOut schema."""
    return UserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        avatar_initials=user.avatar_initials,
        company=user.company,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        worker_profile_id=user.worker_profile.id if user.worker_profile else None,
        supervisor_profile_id=(
            user.supervisor_profile.id if user.supervisor_profile else None
        ),
        team_leader_profile_id=(
            user.team_leader_profile.id if user.team_leader_profile else None
        ),
    )


@router.get("", response_model=list[UserOut])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    actor: User = Depends(_require_owner),
    db: Session = Depends(get_db),
):
    """List all users in the organisation. OWNER only."""
    svc = UserManagementService(db)
    users = svc.list_users(skip=skip, limit=limit)
    return [_build_user_out(u) for u in users]


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: str,
    actor: User = Depends(_require_owner),
    db: Session = Depends(get_db),
):
    """Get a specific user by ID. OWNER only."""
    svc = UserManagementService(db)
    user = svc.get_user(user_id)
    return _build_user_out(user)


@router.post("", response_model=UserOut, status_code=201)
def create_user(
    data: UserCreate,
    actor: User = Depends(_require_owner),
    db: Session = Depends(get_db),
):
    """Create a new user with the appropriate role profile. OWNER only.

    On any validation failure (duplicate email, invalid team, etc.) the
    entire transaction is rolled back and an error is returned.
    """
    svc = UserManagementService(db)
    user = svc.create_user(data, actor)
    return _build_user_out(user)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    data: UserUpdate,
    actor: User = Depends(_require_owner),
    db: Session = Depends(get_db),
):
    """Update allowed fields on a user. OWNER only."""
    svc = UserManagementService(db)
    user = svc.update_user(user_id, data, actor)
    return _build_user_out(user)


@router.post("/{user_id}/activate", response_model=UserOut)
def activate_user(
    user_id: str,
    actor: User = Depends(_require_owner),
    db: Session = Depends(get_db),
):
    """Re-activate a deactivated user. OWNER only."""
    svc = UserManagementService(db)
    user = svc.activate_user(user_id, actor)
    return _build_user_out(user)


@router.post("/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(
    user_id: str,
    actor: User = Depends(_require_owner),
    db: Session = Depends(get_db),
):
    """Deactivate a user (prevents login). OWNER only.

    The user's data is preserved. This is not a deletion.
    Cannot deactivate yourself.
    """
    svc = UserManagementService(db)
    user = svc.deactivate_user(user_id, actor)
    return _build_user_out(user)
