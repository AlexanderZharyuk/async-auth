import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from fastapi import Request, Response
from pydantic import BaseModel
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.postgres import RefreshTokensStorage
from src.v1.auth.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.v1.auth.helpers import (
    generate_jwt,
    generate_user_signature,
    hash_password,
    verify_password,
)
from src.v1.auth.schemas import JWTTokens, User, UserCreate, UserLogin
from src.v1.exceptions import ServiceError
from src.v1.users import models as users_models


class BaseAuthService(ABC):
    """Basic Auth Service class for implementation different auth strategies"""

    @staticmethod
    async def signup(db_session: AsyncSession, user: UserCreate) -> User:
        # FIXME(alexander.zharyuk): Refactor this code (get user from user service method)
        statement = select(users_models.User).filter(
            or_(users_models.User.email == user.email, users_models.User.username == user.username)
        )
        result = await db_session.execute(statement)
        if result.scalar() is not None:
            raise UserAlreadyExistsError()

        user = users_models.User(
            id=uuid.uuid4(),
            **user.model_dump(exclude={"password", "repeat_password", "id"}),
            password=hash_password(user.password),
        )
        user_signature = users_models.UserSignature(
            signature=generate_user_signature(user.username), user_id=user.id
        )

        db_session.add(user)
        db_session.add(user_signature)
        try:
            await db_session.commit()
        except SQLAlchemyError:
            await db_session.rollback()
            raise ServiceError()

        return user

    @abstractmethod
    async def signin(db_session: AsyncSession, data: BaseModel):
        ...

    @abstractmethod
    async def logout(db_session: AsyncSession, current_user=None):
        ...


class JWTAuthService(BaseAuthService):
    """Auth service depends on JWT"""

    @staticmethod
    async def signin(
        db_session: AsyncSession,
        refresh_token_storage: RefreshTokensStorage,
        user: UserLogin,
        request: Request,
        response: Response,
    ) -> JWTTokens:
        # FIXME: Get user from user service method
        statement = select(users_models.User).where(users_models.User.email == user.email)
        result = await db_session.execute(statement)
        if (exists_user := result.scalar()) is None:
            raise UserNotFoundError()

        if not verify_password(user.password, exists_user.password):
            raise UserNotFoundError()

        await __class__._save_login_session_if_not_exists(db_session, exists_user, request)

        # TODO: Add role to JWT
        tokens = generate_jwt(
            payload={"user_id": str(exists_user.id)},
            access_jti=exists_user.signature.signature,
            refresh_jti=uuid.uuid4(),
        )
        await refresh_token_storage.create(db_session, tokens.refresh_token, exists_user.id)
        await __class__._set_user_cookie("access_token", tokens.access_token, response)

        return tokens

    async def logout(db_sessioon: AsyncSession, current_user=None):
        ...

    async def verify(current_user=None):
        ...

    async def terminate_all_sessions(current_user=None):
        ...

    @staticmethod
    async def _save_login_session_if_not_exists(
        db_session: AsyncSession, user: users_models.User, request: Request
    ):
        request_ip = request.client.host
        user_agent = request.headers.get("User-Agent")

        statement = select(users_models.UserLogin).filter(
            and_(
                users_models.UserLogin.user_id == user.id,
                users_models.UserLogin.ip == request_ip,
                users_models.UserLogin.user_agent == user_agent,
            )
        )
        result = await db_session.execute(statement)
        if (exists_login := result.scalar()) is None:
            exists_login = users_models.UserLogin(
                user_id=user.id, ip=request_ip, user_agent=user_agent
            )
        else:
            exists_login.updated_at = datetime.now()

        user.last_login = datetime.now()
        db_session.add(exists_login)
        db_session.add(user)
        try:
            await db_session.commit()
        except SQLAlchemyError:
            await db_session.rollback()
            raise ServiceError()

    @staticmethod
    async def _set_user_cookie(cookie_key: str, cookie_value: str, response: Response):
        response.set_cookie(
            cookie_key,
            cookie_value,
            httponly=settings.jwt_access_token_cookie_httponly,
            secure=settings.jwt_access_token_cookie_secure,
            samesite=settings.jwt_access_token_cookie_samesite,
            max_age=settings.jwt_access_expire_time_in_seconds,
            expires=settings.jwt_access_expire_time_in_seconds
        )


AuthService = JWTAuthService()
