from typing import Annotated
from datetime import datetime
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from jose import jwt
from pydantic import UUID4
from sqlalchemy import delete

from src.core.config import settings
from src.db.storages import Database, BaseStorage
from src.v1.auth.helpers import decode_jwt
from src.v1.users.models import UserRefreshTokens



class PostgresDatabase(Database):
    """Класс БД PostgreSQL"""

    def __init__(self):
        super().__init__(engine=create_async_engine(settings.pg_dsn, future=True))

    async def __call__(self) -> AsyncSession:
        async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            yield session

    async def close(self) -> None:
        await self.engine.dispose()


class RefreshTokenPostgresStorage(BaseStorage):
    @staticmethod
    async def create(db_session: AsyncSession, refresh_token: str, user_id: UUID4) -> UUID4:
        token_headers = jwt.get_unverified_header(refresh_token)
        token_data = decode_jwt(refresh_token)
        refresh_token = UserRefreshTokens(
            token=token_headers.get("jti"),
            user_id=user_id,
            expire_at=datetime.fromtimestamp(token_data.get("exp")),
        )
        db_session.add(refresh_token)
        await db_session.commit()
        return refresh_token.token

    @staticmethod
    async def get(db_session: AsyncSession, token: str) -> UserRefreshTokens:
        # TODO: Make better
        return await db_session.get(UserRefreshTokens, token)

    @staticmethod
    async def delete(db_session: AsyncSession, token: str):
        # TODO: Make better
        statement = delete(UserRefreshTokens).where(UserRefreshTokens.token == token)
        await db_session.execute(statement)
        await db_session.commit()

    @staticmethod
    async def delete_all(db_session: AsyncSession, user_id: UUID4):
        # TODO: Make better
        statement = delete(UserRefreshTokens).where(UserRefreshTokens.user_id == user_id)
        await db_session.execute(statement)
        await db_session.commit()


db_session = PostgresDatabase()
refresh_tokens_storage = RefreshTokenPostgresStorage()
DatabaseSession = Annotated[AsyncSession, Depends(db_session)]
RefreshTokensStorage = Annotated[RefreshTokenPostgresStorage, Depends(refresh_tokens_storage)]

