from typing import Annotated

from redis.asyncio import Redis, from_url
from pydantic import UUID4
from fastapi import Depends

from src.db.storages import BaseStorage
from src.core.config import settings


class RedisBlacklistUserSignatureStorage(BaseStorage):

    def __init__(self) -> None:
        self.protocol: Redis = from_url(
            settings.redis_dsn, 
            decode_responses=True, 
            db=settings.redis_db
        )
        self.namespace: str = "auth_service"

    async def create(self, user_id: UUID4, signature: str):
        signature_key = f"{self.namespace}:{user_id}"
        async with self.protocol.client() as conn:
            await conn.set(signature_key, signature)

    async def get(self, user_id: UUID4) -> str:
        signature_key = f"{self.namespace}:{user_id}"
        async with self.protocol.client() as conn:
            return await conn.get(signature_key)

    async def delete(self, user_id: UUID4):
        signature_key = f"{self.namespace}:{user_id}"
        async with self.protocol.client() as conn:
            return await conn.delete(signature_key)

    async def delete_all(self, user_id: UUID4, count_size: int = 10) -> int:
        pattern = f"{self.namespace}:{user_id}:*"
        cursor = b"0"
        deleted_count = 0

        async with self.protocol.client() as conn:
            while cursor:
                cursor, keys = await conn.scan(cursor, match=pattern, count=count_size)
                deleted_count += await conn.unlink(*keys)
        return deleted_count


redis_blackist_storage = RedisBlacklistUserSignatureStorage()
BlacklistSignatureStorage = Annotated[
    RedisBlacklistUserSignatureStorage, Depends(redis_blackist_storage)
]
