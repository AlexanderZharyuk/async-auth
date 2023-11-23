from abc import ABC
from typing import List, Mapping

from pydantic import UUID4
from sqlalchemy import delete, exc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.exceptions import ServiceError
from src.v1.roles.exceptions import RoleAlreadyExistsError
from src.v1.roles.models import Role, RolesToUsers
from src.v1.roles.schemas import RoleBase
from src.v1.roles.service import PostgreRolesService
from src.v1.users.exceptions import UserNotFound
from src.v1.users.models import User
from src.v1.users.schemas import RoleUser


class BaseUserService(ABC):
    """Basic user service for implement different user services"""

    @staticmethod
    async def get_user(session: AsyncSession, obj_id: int) -> Role:
        """Check if the user exists by id"""
        statement = select(User).where(User.id == obj_id)
        query = await session.execute(statement)
        result = query.scalar_one_or_none()
        if result is None:
            raise UserNotFound
        return result


class PostgreUserService(BaseUserService):
    """User service depends on PostgreSQL"""


class PostgresUserRolesService(BaseUserService):
    """Managing user roles service depends on PostgreSQL"""

    async def get_roles(self, session: AsyncSession, obj_id: UUID4) -> List[RoleBase]:
        await self.get_user(session=session, obj_id=obj_id)
        statement = (
            select(Role)
            .where(RolesToUsers.user_id == obj_id)
            .where(RolesToUsers.role_id == Role.id)
        )
        query = await session.execute(statement)
        result = query.scalars().all()
        roles = [RoleBase.model_validate(role) for role in result]
        return roles

    async def add_role(self, session: AsyncSession, obj_id: UUID4, data: Mapping) -> None:
        role_id = RoleUser(**data).role_id
        await self.get_user(session=session, obj_id=obj_id)
        await PostgreRolesService.get_role(session=session, obj_id=role_id)

        roles_to_users = RolesToUsers(user_id=obj_id, role_id=role_id)
        try:
            session.add(roles_to_users)
            await session.commit()
        except exc.IntegrityError:
            await session.rollback()
            raise RoleAlreadyExistsError
        except exc.SQLAlchemyError:
            await session.rollback()
            raise ServiceError
        return

    async def delete_role(self, session: AsyncSession, obj_id: UUID4, data: Mapping) -> None:
        role_id = RoleUser(**data).role_id
        await self.get_user(session=session, obj_id=obj_id)
        await PostgreRolesService.get_role(session, role_id)

        try:
            statement = (
                delete(RolesToUsers)
                .where(RolesToUsers.role_id == role_id)
                .where(RolesToUsers.user_id == obj_id)
            )
            await session.execute(statement)
            await session.commit()
        except exc.SQLAlchemyError:
            await session.rollback()
            raise ServiceError


UserRolesService = PostgresUserRolesService()
