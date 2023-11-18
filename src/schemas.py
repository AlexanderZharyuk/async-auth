import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BaseResponseBody(BaseModel):
    data: dict | list


class BaseExceptionBody(BaseModel):
    detail: dict | None = None
