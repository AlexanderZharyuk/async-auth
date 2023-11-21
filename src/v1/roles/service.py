from abc import ABC
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from src.db import postgres
from src.db.postgres import PostgresDatabase, get_postgres_storage
from src.v1.roles.models import Role


class BaseRolesService(ABC):
    """Basic roles service for implement different roles services"""


class PostgreRolesService(BaseRolesService):
    """Role service depends on PostgreSQL"""

    session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self):
        data = await self.session.execute(select(Role))
        return data


@lru_cache()
def get_role_service(
    session: AsyncSession,
) -> PostgreRolesService:
    return PostgreRolesService(session)
