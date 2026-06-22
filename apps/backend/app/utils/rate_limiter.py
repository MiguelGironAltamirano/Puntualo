"""app/utils/rate_limiter.py - Rate limiting utilities for reports and other features."""
from __future__ import annotations

import time
from dataclasses import dataclass

from app.utils.cache import redis_client


@dataclass
class RateLimitStatus:
    """Status of a rate limit check."""

    allowed: bool
    remaining: int
    reset_at: float


class ReportRateLimiter:
    """
    Rate limiter for user reports using sliding window algorithm on Redis.
    Prevents abuse by limiting reports per user per hour.
    """

    def __init__(self, max_reports_per_hour: int = 10):
        self.max_reports_per_hour = max_reports_per_hour
        self.window_seconds = 3600  # 1 hour

    def _get_key(self, user_id: str) -> str:
        """Get Redis key for user's report count."""
        return f"report_rate_limit:{user_id}"

    async def check(self, user_id: str) -> RateLimitStatus:
        """
        Check if user can submit a report (sliding window).
        
        Returns:
            RateLimitStatus with allowed flag and remaining quota
        """
        now = time.time()
        key = self._get_key(user_id)

        # Get current list of timestamps
        timestamps = await redis_client.zrange(key, 0, -1, withscores=False)
        
        # Remove old timestamps outside window
        cutoff = now - self.window_seconds
        valid_timestamps = [
            float(ts) for ts in timestamps 
            if float(ts) > cutoff
        ]

        # If we have room for more reports
        if len(valid_timestamps) < self.max_reports_per_hour:
            return RateLimitStatus(
                allowed=True,
                remaining=self.max_reports_per_hour - len(valid_timestamps) - 1,
                reset_at=valid_timestamps[0] + self.window_seconds if valid_timestamps else now + self.window_seconds,
            )

        # Rate limited
        oldest_ts = float(valid_timestamps[0])
        reset_at = oldest_ts + self.window_seconds
        return RateLimitStatus(
            allowed=False,
            remaining=0,
            reset_at=reset_at,
        )

    async def record(self, user_id: str) -> None:
        """Record a new report submission."""
        now = time.time()
        key = self._get_key(user_id)
        
        # Add timestamp to sorted set (score = timestamp)
        await redis_client.zadd(key, {str(now): now})
        
        # Set expiration to window size
        await redis_client.expire(key, self.window_seconds + 1)

    async def reset(self, user_id: str) -> None:
        """Reset user's rate limit (for testing or admin actions)."""
        key = self._get_key(user_id)
        await redis_client.delete(key)


class ReportAbuseDetector:
    """
    Detects abuse of the reporting system (spam reports from single user).
    Uses Redis counter to track false/invalid reports per user.
    """

    def __init__(self, abuse_threshold: int = 5):
        self.abuse_threshold = abuse_threshold
        self.window_seconds = 3600  # 1 hour

    def _get_key(self, user_id: str) -> str:
        """Get Redis key for user's abuse count."""
        return f"report_abuse:{user_id}"

    async def check(self, user_id: str) -> bool:
        """
        Check if user has exceeded abuse threshold.
        
        Returns:
            True if user is detected as abuser, False otherwise
        """
        key = self._get_key(user_id)
        count = await redis_client.get(key)
        return int(count or 0) >= self.abuse_threshold

    async def increment(self, user_id: str) -> int:
        """
        Increment abuse count for user (when they submit invalid report).
        
        Returns:
            New abuse count
        """
        key = self._get_key(user_id)
        count = await redis_client.incr(key)
        
        # Set expiration on first increment
        if count == 1:
            await redis_client.expire(key, self.window_seconds)
        
        return count

    async def reset(self, user_id: str) -> None:
        """Reset user's abuse count (for testing or admin actions)."""
        key = self._get_key(user_id)
        await redis_client.delete(key)
