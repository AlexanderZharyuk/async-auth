import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.db.postgres import db_session
from src.main import app
from src.models import Base


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_engine():
    pg_dsn = (
        f"postgresql+asyncpg://{settings.postgres_user}:"
        f"{settings.postgres_pwd}@{settings.postgres_host}:"
        f"{settings.postgres_port}/"
        f"{settings.postgres_db}_test_db"
    )
    engine = create_async_engine(pg_dsn, future=True, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield conn
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db(db_engine):
    async_session = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def client(db):
    app.dependency_overrides[db_session] = lambda: db
    client = AsyncClient(app=app, base_url="http://api_test")
    yield client
    await client.aclose()
