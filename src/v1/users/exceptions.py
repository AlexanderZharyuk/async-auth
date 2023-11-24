from http import HTTPStatus

from fastapi.exceptions import HTTPException

from src.schemas import BaseExceptionBody


class UserNotFound(HTTPException):
    """Возвращаемая модель при ошибках сервиса."""

    def __init__(
        self, status_code: int = HTTPStatus.NOT_FOUND, message: str = "User not found."
    ) -> None:
        detail = BaseExceptionBody(detail={"code": 6001, "message": message})
        super().__init__(status_code=status_code, detail=detail.model_dump())


class RoleAlreadyEssignedError(HTTPException):
    """Возвращаемая модель при наличии у пользователя роли, который пытается назначить."""

    def __init__(
        self,
        status_code: int = HTTPStatus.BAD_REQUEST,
        message: str = "The user already has a rolewith this name.",
    ) -> None:
        detail = BaseExceptionBody(detail={"code": 5002, "message": message})
        super().__init__(status_code=status_code, detail=detail.model_dump())
