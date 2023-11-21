from abc import ABC
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, AsyncGenerator, Any

from src.db import postgres
from src.db.postgres import PostgresDatabase, get_postgres_storage
from src.v1.roles.models import Role


class BaseRolesService(ABC):
    """Basic roles service for implement different roles services"""


class PostgreRolesService(BaseRolesService):
    """Role service depends on PostgreSQL"""

    def __init__(self, db: AsyncGenerator[AsyncSession, Any]) -> None:
        #db_session = db.get_session()
        self.session = Annotated[AsyncSession, Depends(db)]


    async def get(self):
        data = await self.session.execute(select(Role))
        """stmt = select(Role)
        data = await self.session.execute(stmt)"""
        return None


@lru_cache()
def get_role_service(
    db: Annotated[PostgresDatabase, Depends(get_postgres_storage)],
) -> PostgreRolesService:
    return PostgreRolesService(db())
