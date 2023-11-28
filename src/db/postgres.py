from typing import Annotated
from typing import AsyncGenerator
from datetime import datetime

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError
from jose import jwt, JWTError
from pydantic import UUID4
from sqlalchemy import delete

from src.core.config import settings
from src.v1.exceptions import ServiceError
from src.v1.auth.exceptions import InvalidTokenError
from src.db.storages import Database, BaseStorage
from src.v1.auth.helpers import decode_jwt
from src.v1.users.models import UserRefreshTokens



class PostgresDatabase(Database):
    """Класс БД PostgreSQL"""

    def __init__(self):
        super().__init__(engine=create_async_engine(settings.pg_dsn, future=True))

    async def __call__(self) -> AsyncGenerator[AsyncSession, None]:
        async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session

    async def close(self) -> None:
        await self.engine.dispose()


class PostgresRefreshTokenStorage(BaseStorage):
    """Класс для хранения рефреш-токенов в PostgreSQL"""

    @staticmethod
    async def create(db_session: AsyncSession, refresh_token: str, user_id: UUID4) -> UUID4:
        token_headers = jwt.get_unverified_header(refresh_token)
        try:
            token_payload = decode_jwt(refresh_token)
            await __class__._verify_that_token_is_refresh(token_payload)
        except JWTError:
            raise InvalidTokenError()
        refresh_token = UserRefreshTokens(
            token=token_headers.get("jti"),
            user_id=user_id,
            expire_at=datetime.fromtimestamp(token_payload.get("exp")),
        )
        db_session.add(refresh_token)
        try:
            await db_session.commit()
        except SQLAlchemyError:
            await db_session.rollback()
            raise ServiceError()
        
        return refresh_token.token

    @staticmethod
    async def get(db_session: AsyncSession, token: str) -> UserRefreshTokens:
        # TODO: Make better
        return await db_session.get(UserRefreshTokens, token)

    @staticmethod
    async def delete(db_session: AsyncSession, token: str):
        try:
            token_payload = decode_jwt(token)
            await __class__._verify_that_token_is_refresh(token_payload)
        except JWTError:
            raise InvalidTokenError()
        
        token_headers = jwt.get_unverified_header(token)
        token_id = token_headers.get("jti")
        
        if token_id:
            statement = delete(UserRefreshTokens).where(UserRefreshTokens.token == token_id)
            await db_session.execute(statement)
            try:
                await db_session.commit()
            except SQLAlchemyError:
                await db_session.rollback()

    @staticmethod
    async def delete_all(db_session: AsyncSession, user_id: UUID4):
        statement = delete(UserRefreshTokens).where(UserRefreshTokens.user_id == user_id)
        await db_session.execute(statement)
        try:
            await db_session.commit()
        except SQLAlchemyError:
            await db_session.rollback()

    @staticmethod
    async def _verify_that_token_is_refresh(token_payload: dict):
        if len(token_payload.values()) > 1:
            raise JWTError()


db_session = PostgresDatabase()
refresh_tokens_storage = PostgresRefreshTokenStorage()
DatabaseSession = Annotated[AsyncSession, Depends(db_session)]
RefreshTokensStorage = Annotated[PostgresRefreshTokenStorage, Depends(refresh_tokens_storage)]

