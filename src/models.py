import logging

from pydantic import BaseModel
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)


class BaseResponseBody(BaseModel):
    data: dict | list


class BaseExceptionBody(BaseModel):
    detail: dict | None = None


# Базовый класс для моделей
Base = declarative_base()
