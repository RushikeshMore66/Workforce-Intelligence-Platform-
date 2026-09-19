from fastapi import Depends
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.core.exceptions import PermissionDeniedException
from app.authorization.permissions import Permission
from app.authorization.roles import ROLE_PERMISSIONS

class RequirePermission:
    """Reusable FastAPI dependency for permission-based access control.

    Raises HTTP 403 if the authenticated user's role does not grant the required permission.
    """

    def __init__(self, permission: Permission):
        self.permission = permission

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        user_permissions = ROLE_PERMISSIONS.get(user.role, set())
        if self.permission not in user_permissions:
            raise PermissionDeniedException(
                f"You do not have the required permission ({self.permission.value}) for this operation."
            )
        return user
