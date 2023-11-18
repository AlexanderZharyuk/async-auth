from functools import lru_cache
from logging import config as logging_config

from pydantic_settings import BaseSettings

import src.constants as const
from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    listen_addr: str = "0.0.0.0"
    listen_port: int = 8000
    allowed_hosts: list = const.DEFAULT_ALLOWED_HOSTS
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    db_host: str = "db"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "auth_db"

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def _get_settings():
    return Settings()


settings = _get_settings()
