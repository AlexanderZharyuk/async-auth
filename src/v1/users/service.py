import logging
from typing import List, Type

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.auth.exceptions import PasswordIncorrectError
from src.v1.auth.helpers import hash_password, verify_password
from src.v1.exceptions import ServiceError
from src.v1.users.exceptions import UserNotFound
from src.v1.users.models import User, UserLogin
from src.v1.users.schemas import UserBase, UserUpdate, UserLoginSchema

logger = logging.getLogger(__name__)


class BaseUserService:
    @staticmethod
    async def _get_from_db(db_session: AsyncSession, user_id: UUID4) -> Type[User]:
        user = await db_session.get(User, user_id)
        if not user:
            raise UserNotFound()
        return user

    async def get(self, db_session: AsyncSession, user_id: UUID4) -> UserBase:
        user = await self._get_from_db(db_session=db_session, user_id=user_id)
        return UserBase.model_validate(user)

    async def update(
        self, db_session: AsyncSession, user_id: UUID4, update_data: UserUpdate
    ) -> UserBase:
        user = await self._get_from_db(db_session=db_session, user_id=user_id)

        if update_data.password:
            if not verify_password(update_data.old_password, user.password):
                raise PasswordIncorrectError()
            user.password = hash_password(update_data.password)

        update_data_dict = update_data.model_dump(
            exclude_none=True, exclude={"password", "repeat_password", "old_password"}
        )
        for param, value in update_data_dict.items():
            if value is not None:
                setattr(user, param, value)

        try:
            await db_session.commit()
            await db_session.refresh(user)
        except SQLAlchemyError as ex:
            logger.exception(ex)
            await db_session.rollback()
            raise ServiceError
        return UserBase.model_validate(user)

    async def get_user_login_history(
        self, db_session: AsyncSession, user_id: UUID4, page: int = 1, per_page: int = 50
    ) -> List[UserLoginSchema]:
        limit = per_page * page
        offset = (page - 1) * per_page
        user = await self._get_from_db(db_session=db_session, user_id=user_id)
        logins = await db_session.execute(
            select(UserLogin)
            .where(UserLogin.user_id == user.id)
            .offset(offset)
            .limit(limit)
            .order_by(UserLogin.created_at)
        )
        return [UserLoginSchema.model_validate(login) for login in logins.scalars().all()]


UserService = BaseUserService()
