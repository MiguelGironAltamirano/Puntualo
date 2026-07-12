"""tests/test_report_service.py - Tests for the report service."""
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment, CommentStatus
from app.models.report import Report
from app.modules.evaluations.errors import (
    CommentNotFoundError,
    CommentAlreadyRemovedError,
    ReportRateLimitError,
    ReportAbuseDetectedError,
    ReportDuplicateError,
)
from app.modules.evaluations.service.report_service import ReportService


class TestReportService:
    """Tests for the report service."""

    @pytest.mark.asyncio
    async def test_create_report_success(self, test_db: AsyncSession, test_comment: Comment, test_user):
        """Test successful report creation."""
        service = ReportService(test_db)
        
        # Mock rate limiter to allow
        with patch.object(service.rate_limiter, 'check') as mock_check:
            with patch.object(service.rate_limiter, 'record') as mock_record:
                with patch.object(service.abuse_detector, 'check') as mock_abuse:
                    with patch.object(service, '_calculate_weighted_score') as mock_score:
                        mock_check.return_value = AsyncMock(allowed=True, remaining=9)()
                        mock_check.return_value.allowed = True
                        mock_abuse.return_value = False
                        mock_score.return_value = 0.5
                        
                        result = await service.create(
                            comment_id=str(test_comment.id),
                            user_id=test_user.id,
                            reason="spam",
                            description="Test report",
                        )
                        
                        assert result.comment_id == str(test_comment.id)
                        assert result.reports_count == 1
                        assert result.was_escalated is False

    @pytest.mark.asyncio
    async def test_create_report_rate_limited(self, test_db: AsyncSession, test_comment: Comment, test_user):
        """Test that rate limit is enforced."""
        service = ReportService(test_db)
        
        with patch.object(service.rate_limiter, 'check') as mock_check:
            mock_status = AsyncMock()
            mock_status.allowed = False
            mock_check.return_value = mock_status
            
            with pytest.raises(ReportRateLimitError):
                await service.create(
                    comment_id=str(test_comment.id),
                    user_id=test_user.id,
                    reason="spam",
                    description="Test report",
                )

    @pytest.mark.asyncio
    async def test_create_report_abuse_detected(self, test_db: AsyncSession, test_comment: Comment, test_user):
        """Test that abuse is detected and blocks report."""
        service = ReportService(test_db)
        
        with patch.object(service.rate_limiter, 'check') as mock_check:
            with patch.object(service.abuse_detector, 'check') as mock_abuse:
                mock_status = AsyncMock()
                mock_status.allowed = True
                mock_check.return_value = mock_status
                mock_abuse.return_value = True
                
                with pytest.raises(ReportAbuseDetectedError):
                    await service.create(
                        comment_id=str(test_comment.id),
                        user_id=test_user.id,
                        reason="spam",
                        description="Test report",
                    )

    @pytest.mark.asyncio
    async def test_create_report_comment_not_found(self, test_db: AsyncSession, test_user):
        """Test that non-existent comment raises error."""
        service = ReportService(test_db)
        
        with patch.object(service.rate_limiter, 'check') as mock_check:
            with patch.object(service.abuse_detector, 'check') as mock_abuse:
                mock_status = AsyncMock()
                mock_status.allowed = True
                mock_check.return_value = mock_status
                mock_abuse.return_value = False
                
                with pytest.raises(CommentNotFoundError):
                    await service.create(
                        comment_id=str(uuid.uuid4()),
                        user_id=test_user.id,
                        reason="spam",
                        description="Test report",
                    )

    @pytest.mark.asyncio
    async def test_create_report_escalates_on_high_score(self, test_db: AsyncSession, test_comment: Comment, test_user):
        """Test that comment is escalated when weighted score >= threshold."""
        service = ReportService(test_db)
        
        with patch.object(service.rate_limiter, 'check') as mock_check:
            with patch.object(service.rate_limiter, 'record') as mock_record:
                with patch.object(service.abuse_detector, 'check') as mock_abuse:
                    with patch.object(service, '_calculate_weighted_score') as mock_score:
                        mock_status = AsyncMock()
                        mock_status.allowed = True
                        mock_check.return_value = mock_status
                        mock_abuse.return_value = False
                        # Simulate high weighted score that triggers escalation
                        mock_score.return_value = 5.5
                        
                        result = await service.create(
                            comment_id=str(test_comment.id),
                            user_id=test_user.id,
                            reason="hate_speech",
                            description="Test report",
                        )
                        
                        assert result.was_escalated is True
                        # Comment should be hidden pending review
                        await test_db.refresh(test_comment)
                        assert test_comment.status == CommentStatus.HIDDEN_PENDING_REVIEW.value

    @pytest.mark.asyncio
    async def test_weighted_score_calculation(self, test_db: AsyncSession, test_comment: Comment, test_user):
        """Test weighted score calculation for different reasons."""
        service = ReportService(test_db)
        
        # Create reports with different reasons
        hate_report = Report(
            comment_id=test_comment.id,
            user_id=test_user.id,
            reason="hate_speech",
        )
        spam_report = Report(
            comment_id=test_comment.id,
            user_id=uuid.uuid4(),
            reason="spam",
        )
        test_db.add(hate_report)
        test_db.add(spam_report)
        await test_db.flush()
        
        score = await service._calculate_weighted_score(test_comment)
        
        # Hate speech (2.0) + spam (0.5) = 2.5
        assert score == 2.5
