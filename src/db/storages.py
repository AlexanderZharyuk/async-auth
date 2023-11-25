from abc import ABC, abstractmethod
from typing import Any
from sqlalchemy.ext.asyncio import AsyncEngine


class Database(ABC):
    """Базовый класс объекта базы данных."""

    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError


class BaseStorage(ABC):


    def __call__(self) -> Any:
        return self

    @abstractmethod
    async def create(self):
        ...

    @abstractmethod
    async def get(self, obj_id: str | int):
        ...

    @abstractmethod
    async def delete(self, obj_id: str | int):
        ...

    @abstractmethod
    async def delete_all(self, filter: str | int):
        ...

