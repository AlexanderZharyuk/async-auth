import logging
from abc import ABC, abstractmethod
from typing import List

from pydantic import UUID4
from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.auth.exceptions import PasswordIncorrectError
from src.v1.auth.helpers import hash_password, verify_password
from src.v1.exceptions import ServiceError
from src.v1.roles.models import Role, roles_to_users
from src.v1.roles.schemas import RoleBase
from src.v1.roles.service import RoleService
from src.v1.users.exceptions import (
    UserNotFoundError,
    UserParamsAlreadyOccupied,
    RoleAlreadyAssignedError,
)
from src.v1.users.models import User, UserLogin
from src.v1.users.schemas import UserBase, UserUpdate, UserLoginSchema, RoleUser

logger = logging.getLogger(__name__)


class BaseUserService(ABC):
    @abstractmethod
    async def get(self, *args, **kwargs) -> object:
        raise NotImplementedError

    @abstractmethod
    async def update(self, *args, **kwargs) -> object:
        raise NotImplementedError

    @abstractmethod
    async def get_login_history(self, *args, **kwargs) -> object:
        raise NotImplementedError


class DatabaseUserService(BaseUserService):
    async def get(self, db_session: AsyncSession, attribute: str, attribute_value: str) -> User:
        statement = select(User).where(getattr(User, attribute) == attribute_value)
        result = await db_session.execute(statement)
        if (exists_user := result.scalar()) is None:
            raise UserNotFoundError()
        return exists_user

    async def update(
        self, db_session: AsyncSession, user_id: UUID4, update_data: UserUpdate
    ) -> UserBase:
        user = await self.get(db_session=db_session, attribute="id", attribute_value=user_id)
        if not verify_password(update_data.current_password, user.password):
            raise PasswordIncorrectError()

        conflicts = await db_session.execute(
            select(User)
            .filter(
                or_(
                    User.email == update_data.email,
                    User.username == update_data.username,
                )
            )
            .where(User.id != user_id)
        )
        if conflicts.scalar():
            raise UserParamsAlreadyOccupied()

        if update_data.password:
            user.password = hash_password(update_data.password)

        update_data_dict = update_data.model_dump(
            exclude_none=True, exclude={"password", "repeat_password", "current_password"}
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

    async def get_login_history(
        self, db_session: AsyncSession, user_id: UUID4, page: int = 1, per_page: int = 50
    ) -> List[UserLoginSchema]:
        limit = per_page
        offset = (page - 1) * per_page
        user = await self.get(db_session=db_session, attribute="id", attribute_value=user_id)
        logins = await db_session.execute(
            select(UserLogin)
            .where(UserLogin.user_id == user.id)
            .offset(offset)
            .limit(limit)
            .order_by(UserLogin.created_at)
        )
        return [UserLoginSchema.model_validate(login) for login in logins.scalars()]


class BaseUserRolesService(ABC):
    @abstractmethod
    async def get_roles(self, *args, **kwargs) -> List:
        raise NotImplementedError

    @abstractmethod
    async def add_role(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_role(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    async def has_role(self, *args, **kwargs) -> None:
        raise NotImplementedError


class DatabaseUserRolesService(BaseUserRolesService):
    """Managing user roles service depends on PostgreSQL"""

    async def get_roles(self, session: AsyncSession, user_id: UUID4) -> List:
        await UserService.get(db_session=session, attribute="id", attribute_value=user_id)
        statement = select(Role).join(roles_to_users).filter(roles_to_users.c.user_id == user_id)
        query = await session.execute(statement)
        result = query.scalars().all()
        if result is None:
            return []
        roles = [RoleBase.model_validate(role) for role in result]
        return roles

    async def add_role(self, session: AsyncSession, user_id: UUID4, data: RoleUser) -> None:
        user = await UserService.get(
            db_session=session, attribute="id", attribute_value=user_id
        )
        role = await RoleService.get(session=session, role_id=data.role_id)

        if role in user.roles:
            raise RoleAlreadyAssignedError

        try:
            user.roles.append(role)
            await session.commit()
        except SQLAlchemyError as exc:
            logger.exception(exc)
            await session.rollback()
            raise ServiceError
        return

    async def delete_role(self, session: AsyncSession, user_id: UUID4, role_id: int) -> None:
        user = await UserService.get(
            db_session=session, attribute="id", attribute_value=user_id
        )
        role = await RoleService.get(session=session, role_id=role_id)

        try:
            user.roles.remove(role)
            await session.commit()
        except SQLAlchemyError as exc:
            logger.exception(exc)
            await session.rollback()
            raise ServiceError
        except ValueError as exc:
            logger.exception(exc)
            await session.rollback()
            raise ServiceError

    async def has_role(self, session: AsyncSession, user_id: UUID4, role_id: int) -> bool:
        await UserService.get(db_session=session, attribute="id", attribute_value=user_id)
        statement = (
            select(Role)
            .join(roles_to_users)
            .filter(roles_to_users.c.user_id == user_id)
            .filter(roles_to_users.c.role_id == role_id)
        )
        query = await session.execute(statement)
        result = query.scalars().first()
        return result is not None


UserService = DatabaseUserService()
UserRolesService = DatabaseUserRolesService()
