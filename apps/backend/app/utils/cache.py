from typing import Any, Callable, Awaitable
import redis.asyncio as aioredis
from app.core.config import settings

redis_client: aioredis.Redis = aioredis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


async def get_or_set(key: str, factory: Callable[[], Awaitable[Any]], ttl: int) -> Any:
    cached = await redis_client.get(key)
    if cached is not None:
        return cached
    value = await factory()
    await redis_client.set(key, value, ex=ttl)
    return value


async def incr_with_ttl(key: str, ttl: int) -> int:
    value = await redis_client.incr(key)
    if value == 1:
        await redis_client.expire(key, ttl)
    return value
