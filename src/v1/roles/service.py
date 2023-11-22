from abc import ABC
from functools import lru_cache
from typing import Mapping, List

from sqlalchemy import select, exc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.roles.exceptions import ObjectsNotFound, RoleAlreadyExistsError, RoleNotFound
from src.v1.roles.models import Role
from src.v1.roles.schemas import RoleBase, RoleCreate


class BaseRolesService(ABC):
    """Basic roles service for implement different roles services"""


class PostgreRolesService(BaseRolesService):
    """Role service depends on PostgreSQL"""

    def __init__(self) -> None:
        pass

    async def get_roles(self, session: AsyncSession) -> List[RoleBase]:
        statement = select(Role).order_by(Role.id)
        query = await session.execute(statement)
        result = query.scalars().fetchall()
        await session.close()
        if not result:
            raise ObjectsNotFound
        roles = [RoleBase.model_validate(role) for role in result]
        return roles

    async def create_role(self, session: AsyncSession, data: Mapping) -> RoleBase:
        role_name = RoleCreate(**data).name
        role = Role(name=role_name)
        try:
            session.add(role)
            await session.commit()
            statement = select(Role).where(Role.name == role_name)
            query = await session.execute(statement)
            new_role = query.scalars().one()
            return RoleBase.model_validate(new_role)
        except exc.IntegrityError:
            raise RoleAlreadyExistsError

    async def delete_role(self, session: AsyncSession, obj_id: int) -> RoleBase:
        statement = select(Role).where(Role.id == obj_id)
        try:
            query = await session.execute(statement)
            role = query.scalars().one()
            await session.delete(role)
            await session.commit()
            return RoleBase.model_validate(role)
        except exc.NoResultFound:
            raise RoleNotFound



@lru_cache()
def get_role_service() -> PostgreRolesService:
    return PostgreRolesService()
