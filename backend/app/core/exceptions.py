from fastapi import HTTPException, status


class AuthenticationException(HTTPException):
    """Raised when authentication fails (missing, invalid, or expired credentials).

    Produces HTTP 401 with the standard flat error shape used across the project.
    Use this instead of raising HTTPException(401) directly so the global handler
    can normalize the response.
    """

    def __init__(self, detail: str = "Could not validate credentials."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class EntityNotFoundException(HTTPException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} with id '{entity_id}' not found.",
        )


class PermissionDeniedException(HTTPException):
    def __init__(self, detail: str = "Not enough permissions to perform this action."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class DuplicateEntityException(HTTPException):
    def __init__(self, detail: str = "An entity with the same unique identifier already exists."):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class ValidationException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class BusinessRuleException(HTTPException):
    """Raised when a request is syntactically valid but violates a business rule.

    Use HTTP 400 for simple rule violations and HTTP 409 (DuplicateEntityException)
    for uniqueness conflicts.
    """

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
