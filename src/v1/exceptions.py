from http import HTTPStatus

from fastapi.exceptions import HTTPException

from src.schemas import BaseExceptionBody


class ServiceError(HTTPException):
    """Возвращаемая модель при ошибках сервиса."""

    def __init__(
        self,
        status_code: int = HTTPStatus.BAD_REQUEST,
        message: str = "Service currently unavailable. " "Please try again later.",
    ) -> None:
        detail = BaseExceptionBody(detail={"code": 1001, "message": message})
        super().__init__(status_code=status_code, detail=detail.model_dump())
