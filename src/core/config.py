from functools import lru_cache, cached_property
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
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "auth_db"
    postgres_user: str = "app"
    postgres_pwd: str = "123qwe"

    @cached_property
    def get_pg_dsn(self):
        return (f"postgresql+asyncpg://{self.postgres_user}:"
                f"{self.postgres_pwd}@{self.postgres_host}:"
                f"{self.postgres_port}/{self.postgres_db}")

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def _get_settings():
    return Settings()


settings = _get_settings()
