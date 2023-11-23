from abc import ABC, abstractmethod
from typing import List, Mapping

from sqlalchemy import delete, exc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.roles.exceptions import (
    ColumnNotExist,
    RoleAlreadyExistsError,
    RoleNotFound,
    RolesNotFound,
    ServiceError,
)
from src.v1.roles.models import Role
from src.v1.roles.schemas import RoleBase, RoleCreate, RoleModify


class BaseRolesService(ABC):
    """Basic roles service for implement different roles services"""

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
        if query.scalar() is not None:
            raise RoleAlreadyExistsError

        try:
            session.add(role)
            await session.commit()
            statement = select(Role).where(Role.name == role_name)
            query = await session.execute(statement)
            new_role = query.scalars().one()
            return RoleBase.model_validate(new_role)
        except exc.SQLAlchemyError:
            await session.rolback()
            raise ServiceError

    async def modify_role(self, session: AsyncSession, obj_id: int, data: Mapping) -> RoleBase:
        params = RoleModify(**data)
        statement = select(Role).filter(Role.id == obj_id)
        query = await session.execute(statement)
        if query.scalar() is None:
            raise RoleNotFound

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
            role = query.scalars().one()
            return RoleBase.model_validate(role)
        except exc.IntegrityError:
            await session.rollback()
            raise RoleAlreadyExistsError
        except exc.SQLAlchemyError:
            await session.rollback()
            raise ServiceError

    async def delete_role(self, session: AsyncSession, obj_id: int) -> RoleBase:
        statement = select(Role).where(Role.id == obj_id)
        query = await session.execute(statement)
        if query.scalar() is None:
            raise RoleNotFound

        try:
            statement = delete(Role).where(Role.id == obj_id).returning(Role)
            query = await session.execute(statement)
            await session.commit()
            role = query.scalars().one()
            return RoleBase.model_validate(role)
        except exc.SQLAlchemyError as e:
            print(e)
            await session.rollback()
            raise ServiceError


RoleService = PostgreRolesService()
