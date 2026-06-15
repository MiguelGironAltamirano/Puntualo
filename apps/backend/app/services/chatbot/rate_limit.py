"""Rate limit por usuario para el chatbot (ventana horaria, counter en Redis)."""
from __future__ import annotations

import redis.asyncio as aioredis

from app.core.config import settings

_WINDOW_SECONDS = 3600


def _redis() -> aioredis.Redis:
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def check_and_increment(user_id: str, *, limit: int | None = None, redis_client=None) -> bool:
    """Incrementa el contador horario del usuario. Devuelve True si dentro del límite."""
    limit = limit if limit is not None else settings.CHATBOT_RATE_LIMIT_PER_HOUR
    client = redis_client or _redis()
    key = f"chatbot:ratelimit:{user_id}"
    count = await client.incr(key)
    if count == 1:
        await client.expire(key, _WINDOW_SECONDS)
    return count <= limit
