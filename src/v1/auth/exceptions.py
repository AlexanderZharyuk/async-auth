from http import HTTPStatus

from fastapi.exceptions import HTTPException

from src.schemas import BaseExceptionBody


class UserAlreadyExistsError(HTTPException):
    """Возвращаемая модель при ошибках сервиса."""

    def __init__(
        self,
        status_code: int = HTTPStatus.BAD_REQUEST,
        message: str = "User with provided email or username already exists.",
    ) -> None:
        detail = BaseExceptionBody(detail={"code": 3000, "message": message})
        super().__init__(status_code=status_code, detail=detail.model_dump())


class PasswordIncorrectError(HTTPException):
    """Возвращаемая модель при неправильном пароле."""

    def __init__(
        self,
        status_code: int = HTTPStatus.UNAUTHORIZED,
        message: str = "Incorrect password.",
    ) -> None:
        detail = BaseExceptionBody(detail={"code": 3001, "message": message})
        super().__init__(status_code=status_code, detail=detail.model_dump())
