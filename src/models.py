import logging

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)


# Базовый класс для моделей
class Base(DeclarativeBase):
    pass


class BaseResponseBody(BaseModel):
    data: dict | list


class BaseExceptionBody(BaseModel):
    detail: dict | None = None

