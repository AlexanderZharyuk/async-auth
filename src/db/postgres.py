from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.db.storages import Database


class PostgresDatabase(Database):
    """Класс БД PostgreSQL"""

    session: AsyncSession

    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(client=engine)

    async def __call__(self) -> AsyncGenerator[AsyncSession, None]:
        async_session = async_sessionmaker(
            self.client, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            try:
                yield session
            except:
                await session.rollback()

    async def close(self) -> None:
        await self.client.dispose()


pg: PostgresDatabase | None = None


async def get_postgres_storage() -> PostgresDatabase:
    return pg
