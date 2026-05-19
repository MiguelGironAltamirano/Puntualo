import logging
from typing import Any, Awaitable, Callable

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

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


async def invalidate_professor(professor_id: str) -> None:
    """Invalida las claves de cache del profesor (stub — Tarea 11 lo implementa).

    Tarea 6 lo llama post-commit desde `evaluation_service.create` y
    `report_service.create`. Por ahora solo loggea; Tarea 11 reemplazara el
    cuerpo con DELETEs de las claves conocidas (`professor:{id}:detail`,
    `professor:{id}:comments:default`).
    """
    logger.info("cache.invalidate_professor.stub | professor_id=%s", professor_id)
