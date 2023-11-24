from http import HTTPStatus

from fastapi.exceptions import HTTPException

from src.schemas import BaseExceptionBody


class UserNotFound(HTTPException):
    """Возвращаемая модель при отсутствии пользователя."""

    def __init__(
        self,
        status_code: int = HTTPStatus.NOT_FOUND,
        message: str = "User is not found.",
    ) -> None:
        detail = BaseExceptionBody(
            detail={"code": 2001, "message": message},
        )
        super().__init__(status_code=status_code, detail=detail.model_dump())
