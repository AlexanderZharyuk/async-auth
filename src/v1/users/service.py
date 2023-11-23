import logging
from abc import ABC, abstractmethod
from typing import Mapping, List

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.auth.helpers import hash_password, verify_password
from src.v1.exceptions import ObjectNotFound, ServiceError
from src.v1.users.models import User
from src.v1.users.schemas import UserBase, UserChange, UserLogin

logger = logging.getLogger(__name__)


class BaseUserService(ABC):
    """Basic user service for implement different user services"""

    @staticmethod
    @abstractmethod
    async def get(db_session: AsyncSession, obj_id: UUID4) -> UserBase | dict:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def change(db_session: AsyncSession, obj_id: UUID4, data: Mapping) -> UserBase | dict:
        raise NotImplementedError


class PostgresUserService(BaseUserService):
    """User service depends on PostgreSQL"""

    @staticmethod
    async def get(db_session: AsyncSession, obj_id: UUID4) -> UserBase | dict:
        user = await db_session.get(User, obj_id)
        if not user:
            raise ObjectNotFound(message="User is not found.")
        return UserBase.model_validate(user)

    @staticmethod
    async def change(
        db_session: AsyncSession, obj_id: UUID4, data_to_change_user: UserChange
    ) -> UserBase | dict:
        user = await db_session.get(User, obj_id)
        if not user:
            raise ObjectNotFound(message="User is not found.")

        if data_to_change_user.password:
            if not verify_password(data_to_change_user.old_password, user.password):
                # ToDo: raise PasswordIncorrect exception from auth
                raise ValueError("Incorrect password")
            user.password = hash_password(data_to_change_user.password)

        data_to_change_user_dict = data_to_change_user.model_dump(
            exclude_none=True, exclude={"password", "repeat_password", "old_password"}
        )
        for k, v in data_to_change_user_dict.items():
            if v is not None:
                setattr(user, k, v)

        try:
            await db_session.commit()
            await db_session.refresh(user)
        except SQLAlchemyError as ex:
            logger.exception(ex)
            await db_session.rollback()
            raise ServiceError
        return UserBase.model_validate(user)

    @staticmethod
    async def get_user_login_history(
        db_session: AsyncSession, obj_id: UUID4, page: int = 1, per_page: int = 50
    ) -> List[UserLogin]:
        limit = per_page * page
        offset = (page - 1) * per_page

        # ToDo: implement after login table is implemented
        # user = await db_session.get(User, obj_id)
        # if not user:
        #     raise ObjectNotFound(message="User is not found.")
        #
        # logins = (
        #     await db_session.execute(select(UserLogin).where(UserLogin.user_id == obj_id))
        #     .offset(offset)
        #     .limit(limit)
        #     .order_by(UserLogin.date)
        # )
        # return [UserLogin.model_validate(login) for login in logins.scalars().all()]
        ...


UserService = PostgresUserService()
