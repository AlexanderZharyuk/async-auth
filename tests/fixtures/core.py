import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.db.postgres import db_session
from src.main import app
from src.models import Base
from src.v1.dependencies import require_roles
from src.v1.roles.constants import RolesChoices
from src.v1.roles.models import Role
from src.v1.users.models import User


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_engine():
    pg_dsn = (
        f"postgresql+asyncpg://{settings.postgres_user}:"
        f"{settings.postgres_pwd}@{settings.postgres_host}:"
        f"{settings.postgres_port}/"
        f"{settings.postgres_db}_test_db"
    )
    await create_database()
    engine = create_async_engine(pg_dsn, future=True)
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
    engine = create_async_engine(pg_dsn, future=True).execution_options(
        isolation_level="AUTOCOMMIT"
    )
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
    engine = create_async_engine(pg_dsn, future=True).execution_options(
        isolation_level="AUTOCOMMIT"
    )
    async with engine.connect() as c:
        async with c.begin():
            await c.execute(text(f"DROP DATABASE {settings.postgres_db}_test_db;"))
    await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db(db_engine):
    async_session = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
def get_required_roles():
    async def check_user_roles() -> User:
        super_admin_user_data = {
            "email": "super@admin.com",
            "username": "superadmin",
            "full_name": "superadmin",
        }
        user = User(**super_admin_user_data)
        user.roles = [Role(id=100, name=RolesChoices.ADMIN)]
        return user

    return check_user_roles


@pytest_asyncio.fixture
async def api_session(db: AsyncSession):
    app.dependency_overrides[db_session] = lambda: db
    app.dependency_overrides[require_roles] = lambda: get_required_roles
    client = AsyncClient(app=app, base_url="http://api_test")
    yield client
    await client.aclose()
