from fastapi import status
from fastapi.exceptions import HTTPException


class AuthExceptionCodes:
    """Auth errors codes mapping class"""

    USER_ALREADY_EXISTS: int = 3000
    USER_NOT_FOUND: int = 3001


class UserAlreadyExistsError(HTTPException):
    """Custom error when user already created."""

    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        message: str = "User with provided email or username already exists.",
    ) -> None:
        detail = {"code": AuthExceptionCodes.USER_ALREADY_EXISTS, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class PasswordIncorrectError(HTTPException):
    """Возвращаемая модель при неправильном пароле."""

    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        message: str = "Incorrect password.",
    ) -> None:
        detail = {"code": 3001, "message": message}
        super().__init__(status_code=status_code, detail=detail)
