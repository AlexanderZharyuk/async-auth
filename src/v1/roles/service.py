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

    def __init__(self, session: AsyncSession) -> None:
        db_session = session()
        self.session = Annotated[AsyncSession, Depends(db_session)]

    async def get(self):
        stmt = select(Role)
        data = await self.session.aclose()
        return data


@lru_cache()
def get_role_service(
    session: PostgresDatabase = Depends(get_postgres_storage),
) -> PostgreRolesService:
    return PostgreRolesService(session)
