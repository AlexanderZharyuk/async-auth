from abc import ABC
from typing import List

from pydantic import UUID4
from sqlalchemy import ext, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.users.models import User
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
            raise
        statement = select(Role).where(RolesToUsers.user_id == obj_id).where(RolesToUsers.role_id == Role.id)
        query = await session.execute(statement)
        result = query.scalars().all()
        roles = [RoleBase.model_validate(role) for role in result]
        print(roles)


UserRolesService = PostgresUserRolesService()

