from abc import ABC, abstractmethod
from datetime import datetime
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from jose import jwt
from pydantic import UUID4
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.v1.auth.helpers import decode_jwt
from src.v1.users.models import UserRefreshTokens


class Database(ABC):
    """Базовый класс объекта базы данных."""

    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError


class BaseStorage(ABC):
    @abstractmethod
    async def create():
        ...

    @abstractmethod
    async def get(obj_id: str | int):
        ...

    @abstractmethod
    async def delete(obj_id: str | int):
        ...

    @abstractmethod
    async def delete_all(filter: str | int):
        ...

