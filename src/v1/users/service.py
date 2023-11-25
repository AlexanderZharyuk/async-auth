import logging
from abc import ABC
from typing import List

from pydantic import UUID4
from sqlalchemy import exc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.exceptions import ServiceError
from src.v1.roles.exceptions import RoleAlreadyExistsError
from src.v1.roles.models import Role, roles_to_users
from src.v1.roles.schemas import RoleBase
from src.v1.roles.service import RoleService
from src.v1.users.exceptions import UserNotFound
from src.v1.users.models import User
from src.v1.users.schemas import RoleUser

logger = logging.getLogger(__name__)


class BaseUserService(ABC):
    """Basic user service for implement different user services"""

    @staticmethod
    async def get_user(session: AsyncSession, user_id: int) -> User:
        """Check if the user exists by id"""
        statement = select(User).where(User.id == user_id)
        query = await session.execute(statement)
        result = query.scalar_one_or_none()
        if result is None:
            raise UserNotFound
        return result


class PostgreUserService(BaseUserService):
    """User service depends on PostgreSQL"""


class UserRolesService(BaseUserService):
    """Managing user roles service depends on PostgreSQL"""

    async def get_roles(self, session: AsyncSession, user_id: UUID4) -> List:
        await self.get_user(session=session, user_id=user_id)
        statement = select(Role).join(roles_to_users).filter(roles_to_users.c.user_id == user_id)
        query = await session.execute(statement)
        result = query.scalars().all()
        if result is None:
            return []
        roles = [RoleBase.model_validate(role) for role in result]
        return roles

    async def add_role(self, session: AsyncSession, user_id: UUID4, data: RoleUser) -> None:
        user = await self.get_user(session=session, user_id=user_id)
        role = await RoleService.get_role(session=session, role_id=data.role_id)

        try:
            user.roles.append(role)
            await session.commit()
        except exc.IntegrityError:
            await session.rollback()
            raise RoleAlreadyExistsError
        except exc.SQLAlchemyError as error:
            logger.exception(error)
            await session.rollback()
            raise ServiceError
        return

    async def delete_role(self, session: AsyncSession, user_id: UUID4, data: RoleUser) -> None:
        user = await self.get_user(session=session, user_id=user_id)
        role = await RoleService.get_role(session=session, role_id=data.role_id)

        try:
            user.roles.remove(role)
            await session.commit()
        except exc.SQLAlchemyError as error:
            logger.exception(error)
            await session.rollback()
            raise ServiceError

    async def has_role(self, session: AsyncSession, user_id: UUID4, role_id: int) -> bool:
        await self.get_user(session=session, user_id=user_id)
        statement = (
            select(Role)
            .join(roles_to_users)
            .filter(roles_to_users.c.user_id == user_id)
            .filter(roles_to_users.c.role_id == role_id)
        )
        query = await session.execute(statement)
        result = query.scalars().first()
        return result is not None


UserRolesService = UserRolesService()
