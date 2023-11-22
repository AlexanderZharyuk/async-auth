from abc import ABC, abstractmethod

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.v1.auth import models as auth_models
from src.v1.auth.exceptions import UserAlreadyExistsError
from src.v1.auth.helpers import generate_user_signature, hash_password
from src.v1.auth.schemas import User, UserCreate
from src.v1.users import models as users_models
from src.v1.exceptions import ServiceError


class BaseAuthService(ABC):
    """Basic Auth Service class for implementation different auth strategies"""

    @staticmethod
    async def signup(db_session: AsyncSession, user: UserCreate) -> User:
        # FIXME(alexander.zharyuk): Refactor this code (get user from user service method)
        # TODO: Use db transactions
        statement = select(users_models.User).filter(
            or_(users_models.User.email == user.email, users_models.User.username == user.username)
        )
        result = await db_session.execute(statement)
        if result.scalar() is not None:
            raise UserAlreadyExistsError()

        user = users_models.User(
                **user.model_dump(exclude={"password", "repeat_password", "id"}),
                password=hash_password(user.password),
        )
        db_session.add(user)
        try:
            await db_session.commit()
        except SQLAlchemyError:
            await db_session.rollback()
            raise ServiceError()
        await db_session.refresh(user)

        user_signature = auth_models.UsersSignatures(
            signature=await generate_user_signature(user.username), user_id=user.id
        )
        db_session.add(user_signature)
        try:
            await db_session.commit()
        except SQLAlchemyError:
            await db_session.rollback()
            raise ServiceError

        return user

    @abstractmethod
    async def signin(db_session: AsyncSession):
        ...

    @abstractmethod
    async def logout(db_session: AsyncSession, current_user=None):
        ...


class JWTAuthService(BaseAuthService):
    """Auth service depends on JWT"""

    async def signin(db_session: AsyncSession):
        ...

    async def logout(db_sessioon: AsyncSession, current_user=None):
        ...

    async def verify(current_user=None):
        ...

    async def terminate_all_sessions(current_user=None):
        ...


AuthService = JWTAuthService()
