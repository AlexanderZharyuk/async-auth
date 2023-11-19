from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")


class BaseStorage(ABC):
    # TODO: Подумать над реализацией
    """Базовый класс хранилища."""

    def __init__(self, client: T, **kwargs) -> None:
        self.client = client

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError


class Database(BaseStorage):
    """@abstractmethod
    async def get_session(self) -> AsyncSession:
        raise NotImplementedError"""
