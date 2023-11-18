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
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_db: str = "users_database"
    postgres_user: str = "app"
    postgres_pwd: str = "123qwe"
    pg_dsn: str = f"postgresql+asyncpg://{postgres_user}:{postgres_pwd}@{postgres_host}:{postgres_port}/{postgres_db}"

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def _get_settings():
    return Settings()


settings = _get_settings()
