from abc import ABC


class BaseUserService(ABC):
    """Basic user service for implement different user services"""


class PostgreUserService(BaseUserService):
    """User service depends on PostgreSQL"""

    ...
