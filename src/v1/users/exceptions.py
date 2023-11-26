from http import HTTPStatus

from fastapi.exceptions import HTTPException

class UserNotFoundError(HTTPException):
    """Возвращаемая модель при отсутствии пользователя."""

    def __init__(
        self,
        status_code: int = HTTPStatus.NOT_FOUND,
        message: str = "User is not exists.",
    ) -> None:
        detail = {"code": 2001, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class UserParamsAlreadyOccupied(HTTPException):
    """Возвращаемая модель при отсутствии пользователя."""

    def __init__(
        self,
        status_code: int = HTTPStatus.CONFLICT,
        message: str = "Username or email is already taken.",
    ) -> None:
        detail = {"code": 2002, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class RoleAlreadyEssignedError(HTTPException):
    """Возвращаемая модель при наличии у пользователя роли, которую пытается назначить."""

    def __init__(
        self,
        status_code: int = HTTPStatus.BAD_REQUEST,
        message: str = "The user already has a role with this name.",
    ) -> None:
        detail = {"code": 5002, "message": message}
        super().__init__(status_code=status_code, detail=detail)
