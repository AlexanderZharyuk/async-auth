import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from fastapi import Request, Response
from pydantic import BaseModel, UUID4, ValidationError
from sqlalchemy import and_, or_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from src.core.config import settings
from src.db.postgres import RefreshTokensStorage
from src.v1.auth.exceptions import (
    UserAlreadyExistsError, UnauthorizedError, TokenNotFoundError, InvalidTokenError
)
from src.v1.auth.helpers import (
    generate_jwt,
    generate_user_signature,
    hash_password,
    verify_password,
    decode_jwt,
    validate_jwt
)
from src.v1.auth.schemas import (JWTTokens, User, UserCreate, UserLogin, 
                                 VerifyTokenResponse, JWTPayload)
from src.db.redis import BlacklistSignatureStorage
from src.v1.exceptions import ServiceError
from src.v1.users.service import UserService
from src.v1.users import models as users_models
from src.v1.users.exceptions import UserNotFoundError


class BaseAuthService(ABC):
    """Basic Auth Service class for implementation different auth strategies"""

    @staticmethod
    async def signup(db_session: AsyncSession, user: UserCreate) -> User:
        """Register user in system"""

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
        """
        Login user to service. In response client get pair of JWT-tokens and set client cookie
        with access token.
        """

        exists_user = await UserService.get_by_email(db_session, user.email)
        if not verify_password(user.password, exists_user.password):
            raise UserNotFoundError()

        await __class__._save_login_session_if_not_exists(db_session, exists_user, request)

        # TODO: Add role to JWT
        jwt_payload = JWTPayload(user_id=exists_user.id).model_dump(mode="json")
        tokens = generate_jwt(
            payload=jwt_payload,
            access_jti=exists_user.signature.signature,
            refresh_jti=uuid.uuid4(),
        )
        await refresh_token_storage.create(db_session, tokens.refresh_token, exists_user.id)
        await __class__._set_user_cookie("access_token", tokens.access_token, response)

        return tokens

    @staticmethod
    async def logout(
        db_session: AsyncSession, 
        refresh_token_storage: RefreshTokensStorage,
        response: Response,
        refresh_token: str
    ):
        """Logout user from current session"""

        response.delete_cookie(settings.sessions_cookie_name)
        await refresh_token_storage.delete(db_session, refresh_token)

    @staticmethod
    async def verify(access_token: str, blacklist_signatures_storage: BlacklistSignatureStorage):
        """Verfiy that provided access token is not blacklist"""
        try:
            await validate_jwt(blacklist_signatures_storage, access_token)
            token_payload = decode_jwt(access_token)
            JWTPayload(**token_payload)
            data={"access": True}
        except (UnauthorizedError, ValidationError):
            data = {"access": False}
        return VerifyTokenResponse(data=data)

    @staticmethod
    async def terminate_all_sessions(
        db_session: AsyncSession,
        blacklist_signatures_storage: BlacklistSignatureStorage,
        refresh_token_storage: RefreshTokensStorage,
        response: Response,
        access_token: str
    ):
        """Terminate all sessions"""

        await validate_jwt(blacklist_signatures_storage, access_token)
        response.delete_cookie(settings.sessions_cookie_name)
        try:
            token_payload = decode_jwt(access_token)
        except JWTError:
            raise InvalidTokenError()
        
        token_headers = jwt.get_unverified_header(access_token)
        
        user_id = token_payload.get("user_id")
        old_user_signature = token_headers.get("jti")

        await blacklist_signatures_storage.create(user_id, old_user_signature)
        await __class__._update_user_signature(db_session,  user_id, old_user_signature)

        await refresh_token_storage.delete_all(db_session, user_id=user_id)

    @staticmethod
    async def refresh_tokens(
        db_session: AsyncSession, 
        refresh_token_storage: RefreshTokensStorage,
        response: Response,
        refresh_token: str
    ):
        """Regenerate JWT pair of tokens"""

        try:
            decode_jwt(refresh_token)
        except JWTError:
            raise InvalidTokenError()
        
        refresh_token_headers = jwt.get_unverified_header(refresh_token)
        refresh_jti = refresh_token_headers.get("jti")
        statement = select(users_models.UserRefreshTokens).where(
            users_models.UserRefreshTokens.token == refresh_jti
        )
        result = await db_session.execute(statement)
        if (token := result.scalar()) is None:
            raise TokenNotFoundError()

        user = await UserService.get_by_id(db_session, token.user_id)
        await refresh_token_storage.delete(db_session, refresh_token)

        jwt_payload = JWTPayload(user_id=user.id).model_dump(mode="json")
        tokens = generate_jwt(
            payload=jwt_payload,
            access_jti=user.signature.signature,
            refresh_jti=str(uuid.uuid4()),
        )
        await refresh_token_storage.create(db_session, tokens.refresh_token, user.id)
        await __class__._set_user_cookie(
            settings.sessions_cookie_name, 
            tokens.access_token, 
            response
        )
        return tokens


    @staticmethod
    async def _save_login_session_if_not_exists(
        db_session: AsyncSession, user: users_models.User, request: Request
    ):
        """Save user session if not exists. User sessions identifies by ip and user_agent."""

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
                user_id=user.id, ip=request_ip, user_agent=user_agent, updated_at=datetime.now()
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
        """Set access token to client cookies."""

        response.set_cookie(
            cookie_key,
            cookie_value,
            httponly=settings.jwt_access_token_cookie_httponly,
            secure=settings.jwt_access_token_cookie_secure,
            samesite=settings.jwt_access_token_cookie_samesite,
            max_age=settings.jwt_access_expire_time_in_seconds,
            expires=settings.jwt_access_expire_time_in_seconds
        )

    @staticmethod
    async def _update_user_signature(
        db_session: AsyncSession,
        user_id: UUID4,
        old_user_signature: str
    ):
        """Update user signature when user terminate all sessions."""
        user = await UserService.get_by_id(db_session, user_id)
        new_user_signature = generate_user_signature(user.username)

        statement = update(users_models.UserSignature)\
        .where(users_models.UserSignature.signature == old_user_signature)\
        .values({users_models.UserSignature.signature: new_user_signature})
        await db_session.execute(statement)
        try:
            await db_session.commit()
        except SQLAlchemyError:
            await db_session.rollback()
            raise ServiceError()


AuthService = JWTAuthService()
