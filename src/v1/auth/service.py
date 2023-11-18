from abc import ABC


class BaseAuthService(ABC):
    """Basic Auth Service class for implementation different auth strategies"""

    ...


class JWTAuthService(BaseAuthService):
    """Auth service depends on JWT"""

    ...
