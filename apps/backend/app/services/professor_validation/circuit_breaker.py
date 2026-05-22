from __future__ import annotations

import app.utils.cache as _cache_mod
from app.core.config import settings


class CircuitBreaker:
    """
    Abre una fuente durante CIRCUIT_RESET_SECONDS tras CIRCUIT_THRESHOLD fallos consecutivos.
    Estado persistido en Redis para sobrevivir reinicios del worker.
    """

    def __init__(
        self,
        threshold: int | None = None,
        reset_seconds: int | None = None,
    ) -> None:
        self._threshold = threshold if threshold is not None else settings.CIRCUIT_THRESHOLD
        self._reset_seconds = reset_seconds if reset_seconds is not None else settings.CIRCUIT_RESET_SECONDS

    async def is_open(self, source_name: str) -> bool:
        value = await _cache_mod.redis_client.get(self._key(source_name))
        if value is None:
            return False
        return int(value) >= self._threshold

    async def register_failure(self, source_name: str) -> None:
        key = self._key(source_name)
        new_value = await _cache_mod.redis_client.incr(key)
        if new_value == 1:
            await _cache_mod.redis_client.expire(key, self._reset_seconds)

    @staticmethod
    def _key(source_name: str) -> str:
        return f"circuit:{source_name}:failures"
