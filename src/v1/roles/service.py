from abc import ABC, abstractmethod
from typing import List, Mapping

from sqlalchemy import delete, exc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.exceptions import ServiceError
from src.v1.roles.exceptions import (
    ColumnNotExist,
    RoleAlreadyExistsError,
    RoleNotFound,
    RolesNotFound,
)
from src.v1.roles.models import Role
from src.v1.roles.schemas import RoleBase, RoleCreate, RoleModify


class BaseRolesService(ABC):
    """Basic roles service for implement different roles services"""

    @staticmethod
    async def get_role(session: AsyncSession, obj_id: int) -> Role:
        """Check if the role exists by id"""
        statement = select(Role).where(Role.id == obj_id)
        query = await session.execute(statement)
        result = query.scalar_one_or_none()
        if result is None:
            raise RoleNotFound
        return result


    @abstractmethod
    async def get_roles(self, session: AsyncSession) -> List[RoleBase]:
        ...

    @abstractmethod
    async def create_role(self, session: AsyncSession, data: Mapping) -> RoleBase:
        ...

    @abstractmethod
    async def modify_role(self, session: AsyncSession, obj_id: int, data: Mapping) -> RoleBase:
        ...

    @abstractmethod
    async def delete_role(self, session: AsyncSession, obj_id: int) -> RoleBase:
        ...


class PostgreRolesService(BaseRolesService):
    """Role service depends on PostgreSQL"""

    async def get_roles(self, session: AsyncSession) -> List[RoleBase]:
        statement = select(Role).order_by(Role.id)
        query = await session.execute(statement)
        result = query.scalars().fetchall()
        if not result:
            raise RolesNotFound
        roles = [RoleBase.model_validate(role) for role in result]
        return roles

    async def create_role(self, session: AsyncSession, data: Mapping) -> RoleBase:
        role_name = RoleCreate(**data).name
        role = Role(name=RoleCreate(**data).name)
        statement = select(Role).where(Role.name == role_name)
        query = await session.execute(statement)
        if query.scalar():
            raise RoleAlreadyExistsError

        try:
            session.add(role)
            await session.commit()
            return RoleBase.model_validate(role)
        except exc.SQLAlchemyError:
            await session.rolback()
            raise ServiceError

    async def modify_role(self, session: AsyncSession, obj_id: int, data: Mapping) -> RoleBase:
        params = RoleModify(**data)
        await self.get_role(session, obj_id)

        if hasattr(Role, params.name_column):
            statement = (
                update(Role)
                .where(Role.id == obj_id)
                .values({params.name_column: params.value})
                .returning(Role)
            )
        else:
            raise ColumnNotExist

        try:
            query = await session.execute(statement)
            await session.commit()
            role = query.scalar_one()
            return RoleBase.model_validate(role)
        except exc.IntegrityError:
            await session.rollback()
            raise RoleAlreadyExistsError
        except exc.SQLAlchemyError:
            await session.rollback()
            raise ServiceError

    async def delete_role(self, session: AsyncSession, obj_id: int) -> RoleBase:
        await self.get_role(session, obj_id)

        try:
            statement = delete(Role).where(Role.id == obj_id).returning(Role)
            query = await session.execute(statement)
            await session.commit()
            role = query.scalar_one()
            return RoleBase.model_validate(role)
        except exc.SQLAlchemyError as e:
            await session.rollback()
            raise ServiceError


RoleService = PostgreRolesService()