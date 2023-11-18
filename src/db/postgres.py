from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from src.db.storages import DBStorage

# Базовый класс для моделей
Base = declarative_base()


class PostgresStorage(DBStorage):
    """Класс хранилища PostgreSQL"""

    session: AsyncSession

    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(client=engine)

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


pg: PostgresStorage | None = None


async def get_postgres_storage() -> PostgresStorage:
    return pg
