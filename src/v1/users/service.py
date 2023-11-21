from abc import ABC
from functools import lru_cache
from typing import List, Mapping

from fastapi import Depends
from pydantic import UUID4

from src.db.postgres import PostgresDatabase, get_postgres_storage
from src.v1.exceptions import ObjectNotFound
from src.v1.users.models import User
from src.v1.users.schemas import UserBase, UserLogin


class BaseUserService(ABC):
    """Basic user service for implement different user services"""

    def __init__(
        self,
        storage: PostgresDatabase,
    ) -> None:
        self.storage = storage


class PostgresUserService(BaseUserService):
    """User service depends on PostgreSQL"""

    def __init__(
        self,
        db: PostgresDatabase,
    ) -> None:
        super().__init__(storage=db)

    async def get_user(self, obj_id: UUID4) -> UserBase | dict:
        _session = self.storage()
        session = await anext(_session)
        user = await session.get(User, obj_id)
        await session.close()
        if not user:
            raise ObjectNotFound
        return UserBase.model_validate(user)

    async def change_user(self, obj_id: UUID4, data: Mapping) -> UserBase | dict:
        user = ...
        return UserBase(**user)

    async def get_user_login_history(self, obj_id: UUID4) -> List[UserLogin]:
        user = ...
        return [UserLogin(**user)]


@lru_cache()
def get_user_service(
    db: PostgresDatabase = Depends(get_postgres_storage),
) -> PostgresUserService:
    return PostgresUserService(db)
