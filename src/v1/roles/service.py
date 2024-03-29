from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List

from sqlalchemy import delete, exc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.v1.exceptions import ServiceError
from src.v1.roles.exceptions import RoleAlreadyExistsError, RoleNotFound
from src.v1.roles.models import Role
from src.v1.roles.schemas import RoleBase, RoleCreate, RoleUpdate

logger = logging.getLogger(__name__)


class BaseRoleService(ABC):
    @abstractmethod
    async def get(self, *args, **kwargs) -> object:
        raise NotImplementedError

    @abstractmethod
    async def list(self, *args, **kwargs) -> object:
        raise NotImplementedError

    @abstractmethod
    async def create(self, *args, **kwargs) -> object:
        raise NotImplementedError

    @abstractmethod
    async def update(self, *args, **kwargs) -> object:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *args, **kwargs) -> object:
        raise NotImplementedError


class DatabaseRoleService(BaseRoleService):
    """Role service depends on PostgreSQL"""

    async def get(self, session: AsyncSession, role_id: int) -> Role:
        """Check if the role exists by id"""
        statement = select(Role).where(Role.id == role_id)
        query = await session.execute(statement)
        result = query.scalar_one_or_none()
        if result is None:
            raise RoleNotFound
        return result

    async def list(self, session: AsyncSession) -> List[RoleBase] | dict:
        statement = select(Role).order_by(Role.id)
        query = await session.execute(statement)
        result = query.scalars().fetchall()
        if not result:
            return {}
        roles = [RoleBase.model_validate(role) for role in result]
        return roles

    async def create(self, session: AsyncSession, data: RoleCreate) -> RoleBase:
        role = Role(name=data.name)
        statement = select(Role).where(Role.name == data.name)
        query = await session.execute(statement)
        if query.scalar():
            raise RoleAlreadyExistsError

        try:
            session.add(role)
            await session.commit()
            return RoleBase.model_validate(role)
        except exc.SQLAlchemyError as error:
            logger.exception(error)
            await session.rollback()
            raise ServiceError

    async def update(self, session: AsyncSession, role_id: int, data: RoleUpdate) -> RoleBase:
        await self.get(session=session, role_id=role_id)

        statement = (
            update(Role).where(Role.id == role_id).values({Role.name: data.name}).returning(Role)
        )

        try:
            query = await session.execute(statement)
            await session.commit()
            role = query.scalar_one()
            return RoleBase.model_validate(role)
        except exc.IntegrityError:
            await session.rollback()
            raise RoleAlreadyExistsError
        except exc.SQLAlchemyError as error:
            logger.exception(error)
            await session.rollback()
            raise ServiceError

    async def delete(self, session: AsyncSession, role_id: int) -> bool:
        await self.get(session=session, role_id=role_id)

        try:
            statement = delete(Role).where(Role.id == role_id).returning(Role)
            await session.execute(statement)
            await session.commit()
            return True
        except exc.SQLAlchemyError as error:
            logger.exception(error)
            await session.rollback()
            raise ServiceError


RoleService = DatabaseRoleService()
