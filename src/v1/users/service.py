from abc import ABC
from typing import List, Mapping

from pydantic import UUID4
from sqlalchemy import exc, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.exceptions import ServiceError
from src.v1.users.exceptions import UserNotFound
from src.v1.roles.exceptions import RoleNotFound
from src.v1.users.models import User
from src.v1.users.schemas import RoleUser
from src.v1.roles.models import Role, RolesToUsers
from src.v1.roles.schemas import RoleBase


class BaseUserService(ABC):
    """Basic user service for implement different user services"""


class PostgreUserService(BaseUserService):
    """User service depends on PostgreSQL"""

class PostgresUserRolesService(BaseUserService):
    """Managing user roles service depends on PostgreSQL"""

    async def get_roles(self, session: AsyncSession, obj_id: UUID4) -> List[RoleBase]:
        statement = select(User).where(User.id == obj_id)
        query = await session.execute(statement)
        if query.scalar() is None:
            raise UserNotFound
        statement = select(Role).where(RolesToUsers.user_id == obj_id).where(RolesToUsers.role_id == Role.id)
        query = await session.execute(statement)
        result = query.scalars().all()
        roles = [RoleBase.model_validate(role) for role in result]
        return roles

    async def add_role(self, session: AsyncSession, user_id: UUID4, data: Mapping) -> None:
        role_id = RoleUser(**data).role_id
        #ToDo: add method check User
        statement = select(User).where(User.id == user_id)
        query = await session.execute(statement)
        if query.scalar() is None: raise UserNotFound

        statement = select(Role).where(Role.id == role_id)
        query = await session.execute(statement)
        if query.scalar() is None: raise RoleNotFound

        roles_to_users = RolesToUsers(user_id=user_id, role_id=role_id)
        try:
            session.add(roles_to_users)
            await session.commit()
        except exc.SQLAlchemyError:
            await session.rollback()
            raise ServiceError
        return


UserRolesService = PostgresUserRolesService()

