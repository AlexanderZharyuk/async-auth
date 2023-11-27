import pytest_asyncio

from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.main import app
from src.db.postgres import db_session
from src.core.config import settings
from src.models import Base


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_engine():
    pg_dsn = (
        f"postgresql+asyncpg://{settings.postgres_user}:"
        f"{settings.postgres_pwd}@{settings.postgres_host}:"
        f"{settings.postgres_port}/"
        f"{settings.postgres_db}_test_db"
    )
    await create_database()
    engine = create_async_engine(pg_dsn, future=True, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield conn
    await engine.dispose()
    await delete_database()

async def create_database():
    pg_dsn = (
        f"postgresql+asyncpg://{settings.postgres_user}:"
        f"{settings.postgres_pwd}@{settings.postgres_host}:"
        f"{settings.postgres_port}/postgres"
    )
    engine = create_async_engine(pg_dsn, future=True, echo=True).execution_options(isolation_level="AUTOCOMMIT")
    async with engine.connect() as c:
        async with c.begin():
            await c.execute(text(f"CREATE DATABASE {settings.postgres_db}_test_db;"))
    await engine.dispose()


async def delete_database():
    pg_dsn = (
        f"postgresql+asyncpg://{settings.postgres_user}:"
        f"{settings.postgres_pwd}@{settings.postgres_host}:"
        f"{settings.postgres_port}/postgres"
    )
    engine = create_async_engine(pg_dsn, future=True, echo=True).execution_options(isolation_level="AUTOCOMMIT")
    async with engine.connect() as c:
        async with c.begin():
            await c.execute(text(f"DROP DATABASE {settings.postgres_db}_test_db;"))
    await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db(db_engine):
    async_session = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def api_session(db: AsyncSession):
    app.dependency_overrides[db_session] = lambda: db
    client = AsyncClient(app=app, base_url="http://api_test")
    yield client
    await client.aclose()