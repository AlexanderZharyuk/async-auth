import asyncio
import pytest
import pytest_asyncio

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
#ToDo: Брать настройки из файла для тестов (путь подключения к тестовой БД)
from src.core.config import settings

from src.main import app

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def api_session():
    client = AsyncClient(app=app, base_url="http://api_test")
    yield client
    await client.aclose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_session():
    engine = create_async_engine(settings.pg_dsn, future=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session = async_session()
    yield session
    await session.close()