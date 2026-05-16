from __future__ import annotations

import logging
from calendar import monthrange
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class BudgetExhausted(Exception):
    pass


class BudgetTracker:
    """
    Contador mensual atómico en Redis. Garantiza nunca rebasar el límite oficial.

    Claves Redis:
    - tavily:budget:{YYYY-MM}       → contador de calls del mes (prod)
    - tavily:budget:dev:{YYYY-MM}   → contador separado para dev/smoke tests
    """

    HARD_CAP_PROD = 950
    HARD_CAP_DEV = 50
    SOFT_WARNING_PROD = 760

    def __init__(self, redis_client, env: str = "prod") -> None:
        self._redis = redis_client
        self._env = env
        self._cap = self.HARD_CAP_PROD if env == "prod" else self.HARD_CAP_DEV
        self._warning = self.SOFT_WARNING_PROD if env == "prod" else None

    def _current_key(self) -> str:
        ym = datetime.now(timezone.utc).strftime("%Y-%m")
        prefix = "tavily:budget:dev:" if self._env != "prod" else "tavily:budget:"
        return f"{prefix}{ym}"

    def _seconds_until_month_end(self) -> int:
        now = datetime.now(timezone.utc)
        last_day = monthrange(now.year, now.month)[1]
        end_of_month = now.replace(day=last_day, hour=23, minute=59, second=59)
        return max(1, int((end_of_month - now).total_seconds()))

    async def try_consume(self, n: int = 1) -> bool:
        """
        Atómico: INCRBY + comparar. Si supera el cap, DECRBY y retorna False.
        Garantiza que NUNCA se gaste 1 call de más.
        """
        key = self._current_key()
        new_value = await self._redis.incrby(key, n)

        if new_value == n:
            # Primera llamada del mes: establecer TTL
            ttl = self._seconds_until_month_end()
            await self._redis.expire(key, ttl)

        if new_value > self._cap:
            await self._redis.decrby(key, n)
            return False

        if self._warning and new_value >= self._warning:
            logger.warning(
                f"Tavily budget at {new_value}/{self._cap} "
                f"({new_value / self._cap * 100:.0f}%)"
            )

        return True

    async def current_usage(self) -> int:
        key = self._current_key()
        value = await self._redis.get(key)
        return int(value) if value else 0
