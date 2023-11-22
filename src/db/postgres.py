from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.core.config import settings
from src.db.storages import Database


class PostgresDatabase(Database):
    """Класс БД PostgreSQL"""

    def __init__(self):
        super().__init__(engine=create_async_engine(settings.pg_dsn, future=True))

    async def __call__(self) -> AsyncSession:
        async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
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
        await self.engine.dispose()


db_session = PostgresDatabase()
DatabaseSession = Annotated[AsyncSession, Depends(db_session)]
