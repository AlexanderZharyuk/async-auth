from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from src.db.storages import Database

# Базовый класс для моделей
Base = declarative_base()


class PostgresDatabase(Database):
    """Класс БД PostgreSQL"""

    session: AsyncSession

    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(client=engine)

    async def __call__(self) -> AsyncSession:
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            try:
                yield session
            except:
                await session.rollback()

    # Dependency для сервисов
    async def get_session(self) -> AsyncSession:
        async_session = sessionmaker(client, class_=AsyncSession, expire_on_commit=False)
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
