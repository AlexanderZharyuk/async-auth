from fastapi import status
from fastapi.exceptions import HTTPException


class AuthExceptionCodes:
    """Auth errors codes mapping class"""

    USER_ALREADY_EXISTS: int = 3000
    USER_NOT_FOUND: int = 3001
    USER_UNAUTHORIZED: int = 3002
    PROVIDED_PASSWORD_INCORRECT: int = 3003
    INVALID_PROVIDED_TOKEN: int = 3004


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
    """Custom error when provided password is incorrect."""

    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        message: str = "Incorrect password.",
    ) -> None:
        detail = {"code": AuthExceptionCodes.PROVIDED_PASSWORD_INCORRECT, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class UnauthorizedError(HTTPException):
    """Custom unauthorized error."""

    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        message: str = "User unauthorized.",
    ) -> None:
        detail = {"code": AuthExceptionCodes.USER_UNAUTHORIZED, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class InvalidTokenError(HTTPException):
    """Custom unauthorized error."""

    def __init__(
        self,
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
        message: str = "Invalid token.",
    ) -> None:
        detail = {"code": AuthExceptionCodes.INVALID_PROVIDED_TOKEN, "message": message}
        super().__init__(status_code=status_code, detail=detail)
