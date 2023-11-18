from abc import ABC


class BaseRolesService(ABC):
    """Basic roles service for implement different roles services"""


class PostgreRolesService(BaseRolesService):
    """Role service depends on PostgreSQL"""

    ...
