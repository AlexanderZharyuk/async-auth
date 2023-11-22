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
        detail = BaseExceptionBody(detail={"code": 5000, "message": message})
        super().__init__(status_code=status_code, detail=detail.model_dump())


class ObjectsNotFound(HTTPException):
    """Возвращаемая модель при ошибках сервиса."""

    def __init__(self, status_code: int = HTTPStatus.NOT_FOUND, message: str = "Objects doesn't exists") -> None:
        detail = BaseExceptionBody(detail={"code": 5001, "message": message})
        super().__init__(status_code=status_code, detail=detail.model_dump())

class RoleAlreadyExistsError(HTTPException):
    """Возвращаемая модель при ошибках сервиса."""

    def __init__(
            self,
            status_code: int = HTTPStatus.BAD_REQUEST,
            message: str = "Role with name already exists.",
    ) -> None:
        detail = BaseExceptionBody(detail={"code": 5002, "message": message})
        super().__init__(status_code=status_code, detail=detail.model_dump())

class RoleNotFound(HTTPException):
    """Возвращаемая модель при ошибках сервиса."""

    def __init__(self, status_code: int = HTTPStatus.NOT_FOUND, message: str = "Role with name not found.") -> None:
        detail = BaseExceptionBody(detail={"code": 5003, "message": message})
        super().__init__(status_code=status_code, detail=detail.model_dump())
