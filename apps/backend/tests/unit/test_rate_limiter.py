"""tests/test_rate_limiter.py - Tests for report rate limiting."""
import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.utils.rate_limiter import ReportRateLimiter, ReportAbuseDetector


class TestReportRateLimiter:
    """Tests for the report rate limiter."""

    @pytest.mark.asyncio
    async def test_first_report_allowed(self):
        """Test that first report is always allowed."""
        limiter = ReportRateLimiter(max_reports_per_hour=10)
        
        with patch('app.utils.rate_limiter.redis_client') as mock_redis:
            # Empty list means no prior reports
            mock_redis.zrange = AsyncMock(return_value=[])
            
            status = await limiter.check("user-123")
            
            assert status.allowed is True
            assert status.remaining == 9

    @pytest.mark.asyncio
    async def test_within_limit(self):
        """Test that reports within limit are allowed."""
        limiter = ReportRateLimiter(max_reports_per_hour=10)
        now = time.time()
        
        with patch('app.utils.rate_limiter.redis_client') as mock_redis:
            # Simulate 5 recent reports (within window)
            recent_timestamps = [
                str(now - 100),
                str(now - 200),
                str(now - 300),
                str(now - 400),
                str(now - 500),
            ]
            mock_redis.zrange = AsyncMock(return_value=recent_timestamps)
            
            status = await limiter.check("user-123")
            
            assert status.allowed is True
            assert status.remaining == 4  # 10 - 5 - 1 = 4

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self):
        """Test that rate limit is enforced."""
        limiter = ReportRateLimiter(max_reports_per_hour=3)
        now = time.time()
        
        with patch('app.utils.rate_limiter.redis_client') as mock_redis:
            # Simulate 3 existing reports (at limit)
            full_timestamps = [
                str(now - 100),
                str(now - 200),
                str(now - 300),
            ]
            mock_redis.zrange = AsyncMock(return_value=full_timestamps)
            
            status = await limiter.check("user-123")
            
            assert status.allowed is False
            assert status.remaining == 0

    @pytest.mark.asyncio
    async def test_record_report(self):
        """Test that report is recorded in Redis."""
        limiter = ReportRateLimiter(max_reports_per_hour=10)
        
        with patch('app.utils.rate_limiter.redis_client') as mock_redis:
            mock_redis.zadd = AsyncMock()
            mock_redis.expire = AsyncMock()
            
            await limiter.record("user-123")
            
            # Verify zadd and expire were called
            assert mock_redis.zadd.called
            assert mock_redis.expire.called

    @pytest.mark.asyncio
    async def test_old_timestamps_filtered_out(self):
        """Test that timestamps outside window are ignored."""
        limiter = ReportRateLimiter(max_reports_per_hour=10)
        now = time.time()
        old_cutoff = now - 3600  # Outside window
        
        with patch('app.utils.rate_limiter.redis_client') as mock_redis:
            # Mix of old and recent timestamps
            mixed_timestamps = [
                str(old_cutoff - 100),  # Old, should be filtered
                str(now - 100),  # Recent
                str(now - 200),  # Recent
            ]
            mock_redis.zrange = AsyncMock(return_value=mixed_timestamps)
            
            status = await limiter.check("user-123")
            
            # Only 2 recent reports count
            assert status.allowed is True
            assert status.remaining == 7  # 10 - 2 - 1 = 7


class TestReportAbuseDetector:
    """Tests for report abuse detection."""

    @pytest.mark.asyncio
    async def test_no_abuse_initially(self):
        """Test that new users are not flagged as abusers."""
        detector = ReportAbuseDetector(abuse_threshold=5)
        
        with patch('app.utils.rate_limiter.redis_client') as mock_redis:
            mock_redis.get = AsyncMock(return_value=None)
            
            is_abuser = await detector.check("user-123")
            
            assert is_abuser is False

    @pytest.mark.asyncio
    async def test_abuse_detection_at_threshold(self):
        """Test that users at abuse threshold are flagged."""
        detector = ReportAbuseDetector(abuse_threshold=5)
        
        with patch('app.utils.rate_limiter.redis_client') as mock_redis:
            mock_redis.get = AsyncMock(return_value="5")
            
            is_abuser = await detector.check("user-123")
            
            assert is_abuser is True

    @pytest.mark.asyncio
    async def test_increment_abuse_count(self):
        """Test that abuse count is incremented."""
        detector = ReportAbuseDetector(abuse_threshold=5)
        
        with patch('app.utils.rate_limiter.redis_client') as mock_redis:
            mock_redis.incr = AsyncMock(return_value=3)
            mock_redis.expire = AsyncMock()
            
            count = await detector.increment("user-123")
            
            assert count == 3
            assert mock_redis.incr.called

    @pytest.mark.asyncio
    async def test_reset_abuse_count(self):
        """Test that abuse count can be reset."""
        detector = ReportAbuseDetector(abuse_threshold=5)
        
        with patch('app.utils.rate_limiter.redis_client') as mock_redis:
            mock_redis.delete = AsyncMock()
            
            await detector.reset("user-123")
            
            assert mock_redis.delete.called
