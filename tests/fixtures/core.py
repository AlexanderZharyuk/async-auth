import uuid

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.db.postgres import db_session
from src.main import app
from src.models import Base
from src.v1.auth.helpers import (
    generate_jwt,
    hash_password,
)
from src.v1.users.models import User

pg_connect_string = (
    f"postgresql+asyncpg://{settings.postgres_user}:"
    f"{settings.postgres_password}@{settings.postgres_host}:"
    f"{settings.postgres_port}/"
)


async def create_database():
    pg_dsn = f"{pg_connect_string}postgres"
    engine = create_async_engine(pg_dsn, future=True).execution_options(
        isolation_level="AUTOCOMMIT"
    )
    async with engine.connect() as c:
        async with c.begin():
            await c.execute(text(f"CREATE DATABASE {settings.postgres_db}_test_db;"))
    await engine.dispose()


async def delete_database():
    pg_dsn = f"{pg_connect_string}postgres"
    engine = create_async_engine(pg_dsn, future=True).execution_options(
        isolation_level="AUTOCOMMIT"
    )
    async with engine.connect() as c:
        async with c.begin():
            await c.execute(text(f"DROP DATABASE IF EXISTS {settings.postgres_db}_test_db;"))
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    pg_dsn = f"{pg_connect_string}{settings.postgres_db}_test_db"
    await delete_database()
    await create_database()
    engine = create_async_engine(pg_dsn, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield conn
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def db(db_engine):
    async_session = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def super_admin_access_token(db):
    user = User(
        **{
            "id": str(uuid.uuid4()),
            "username": "superadmin",
            "email": "super@admin.com",
            "full_name": "superadmin",
            "is_superuser": True,
            "password": hash_password("superadmin_password"),
        }
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    tokens = generate_jwt(
        payload={"user_id": str(user.id), "roles": []},
        access_jti=str(uuid.uuid4()),
        refresh_jti=uuid.uuid4(),
    ).model_dump(mode="json")
    yield tokens["access_token"]


@pytest_asyncio.fixture
async def api_session(db: AsyncSession, super_admin_access_token: str):
    app.dependency_overrides[db_session] = lambda: db
    client = AsyncClient(
        app=app,
        cookies={"access_token": super_admin_access_token},
        base_url="http://api_test"
    )
    yield client
    await client.aclose()
