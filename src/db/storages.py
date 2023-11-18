from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import UUID4

T = TypeVar("T")


class BaseStorage(ABC):
    # TODO: Подумать над реализацией
    """Базовый класс хранилища."""

    def __init__(self, client: T, **kwargs) -> None:
        self.client = client

    @abstractmethod
    async def get(self, obj_id: UUID4 | str | int | None, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError
