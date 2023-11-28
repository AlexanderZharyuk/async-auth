from http import HTTPStatus

from fastapi.exceptions import HTTPException


class UserExceptionCodes:
    """Auth errors codes mapping class"""

    USER_NOT_FOUND: int = 2001
    USER_PARAMS_CONFLICT: int = 2002
    ROLE_ALREADY_ASSIGNED: int = 2003
    PASSWORDS_DO_NOT_MATCH: int = 2004


class UserNotFoundError(HTTPException):
    """Возвращаемая модель при отсутствии пользователя."""

    def __init__(
        self,
        status_code: int = HTTPStatus.NOT_FOUND,
        message: str = "User is not exists.",
    ) -> None:
        detail = {"code": UserExceptionCodes.USER_NOT_FOUND, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class UserParamsAlreadyOccupied(HTTPException):
    """Возвращаемая модель при отсутствии пользователя."""

    def __init__(
        self,
        status_code: int = HTTPStatus.CONFLICT,
        message: str = "Username or email is already taken.",
    ) -> None:
        detail = {"code": UserExceptionCodes.USER_PARAMS_CONFLICT, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class RoleAlreadyAssignedError(HTTPException):
    """Возвращаемая модель при наличии у пользователя роли, которую пытается назначить."""

    def __init__(
        self,
        status_code: int = HTTPStatus.BAD_REQUEST,
        message: str = "The user already has a role with this name.",
    ) -> None:
        detail = {"code": UserExceptionCodes.ROLE_ALREADY_ASSIGNED, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class PasswordsDoNotMatch(HTTPException):
    """Возвращаемая модель при наличии у пользователя роли, которую пытается назначить."""

    def __init__(
        self,
        status_code: int = HTTPStatus.UNAUTHORIZED,
        message: str = "Passwords do not match.",
    ) -> None:
        detail = {"code": UserExceptionCodes.PASSWORDS_DO_NOT_MATCH, "message": message}
        super().__init__(status_code=status_code, detail=detail)
