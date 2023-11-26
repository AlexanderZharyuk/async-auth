from functools import cached_property, lru_cache
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

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "auth_db"
    postgres_user: str = "app"
    postgres_pwd: str = "123qwe"

    jwt_secret_key: str = "50ae6b6f23a914d61c65b7bf6124107d73b47e0303c4da828c06092d1a18b056"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_time_in_seconds: int = 60 * 15  # 15 minutes
    jwt_refresh_expire_time_in_seconds: int = 60 * 60 * 24 * 14  # 14 days
    jwt_access_token_cookie_samesite: str = "lax"
    jwt_access_token_cookie_httponly: bool = True
    jwt_access_token_cookie_secure: bool = True

    @cached_property
    def pg_dsn(self):
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_pwd}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def _get_settings():
    return Settings()


settings = _get_settings()
