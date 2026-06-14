"""app/modules/evaluations/service/report_service.py"""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.comment import Comment, CommentStatus
from app.models.report import Report, ReportReason, ReportStatus
from app.models.user import User
from app.modules.evaluations.errors import (
    CommentNotFoundError,
    CommentAlreadyRemovedError,
    ReportDuplicateError,
    ReportRateLimitError,
    ReportAbuseDetectedError,
)
from app.utils.rate_limiter import ReportRateLimiter, ReportAbuseDetector


@dataclass
class ReportResult:
    comment_id: str
    reports_count: int
    was_escalated: bool = False


# Weighted scores for different report reasons (higher = more serious)
REASON_WEIGHTS = {
    ReportReason.HATE_SPEECH.value: 2.0,
    ReportReason.HARASSMENT.value: 2.0,
    ReportReason.FALSE_INFORMATION.value: 1.5,
    ReportReason.PRIVACY_VIOLATION.value: 2.0,
    ReportReason.SPAM.value: 0.5,
    ReportReason.IMPERSONATION.value: 1.5,
    ReportReason.OFF_TOPIC.value: 0.3,
    ReportReason.OTHER.value: 0.5,
}


class ReportService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.rate_limiter = ReportRateLimiter(
            max_reports_per_hour=settings.REPORT_RATE_LIMIT_PER_HOUR
        )
        self.abuse_detector = ReportAbuseDetector(
            abuse_threshold=settings.REPORT_ABUSE_THRESHOLD
        )

    async def create(
        self,
        *,
        comment_id: str,
        user_id: uuid.UUID,
        reason: str,
        description: str | None,
    ) -> ReportResult:
        """
        Create a report for a comment with rate limiting and abuse detection.
        
        Flow:
        1. Check rate limit (max 10 reports/hour per user)
        2. Detect abuse (5+ flagged reports in hour -> blocked)
        3. Verify comment exists and is published
        4. Check if already removed
        5. Create report and increment counter
        6. Calculate weighted score and trigger moderation if >= 5.0
        
        Raises:
            ReportRateLimitError: User exceeded hourly report quota
            ReportAbuseDetectedError: User flagged for abusing report system
            CommentNotFoundError: Comment doesn't exist or not published
            CommentAlreadyRemovedError: Comment was already removed
            ReportDuplicateError: User already reported this comment
        """
        
        # Step 1: Check rate limit
        rate_status = await self.rate_limiter.check(str(user_id))
        if not rate_status.allowed:
            raise ReportRateLimitError()
        
        # Step 2: Check abuse detection
        is_abuser = await self.abuse_detector.check(str(user_id))
        if is_abuser:
            raise ReportAbuseDetectedError()
        
        # Step 3: Verify comment exists and is published
        comment = await self.db.get(Comment, uuid.UUID(str(comment_id)))
        if comment is None or comment.status != CommentStatus.PUBLISHED.value:
            raise CommentNotFoundError()
        
        # Step 4: Check if already removed (reports only work on published comments)
        if comment.status == CommentStatus.REMOVED.value:
            raise CommentAlreadyRemovedError()
        
        # Step 5: Create report
        report = Report(
            comment_id=comment.id,
            user_id=user_id,
            reason=reason,
            description=description,
            escalated=False,
        )
        self.db.add(report)
        
        try:
            await self.db.flush()
        except IntegrityError as exc:
            await self.db.rollback()
            raise ReportDuplicateError() from exc
        
        # Step 6: Update comment report count
        comment.reports_count += 1
        
        # Step 7: Calculate weighted score and check if should escalate
        weighted_score = await self._calculate_weighted_score(comment)
        was_escalated = False
        
        if weighted_score >= settings.REPORT_MODERATION_TRIGGER_THRESHOLD:
            report.escalated = True
            was_escalated = True
            # Mark comment for AI moderation review (set to pending_review status)
            if comment.status == CommentStatus.PUBLISHED.value:
                comment.status = CommentStatus.HIDDEN_PENDING_REVIEW.value
        
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(comment)
        
        # Record this report submission in rate limit tracker
        await self.rate_limiter.record(str(user_id))
        
        return ReportResult(
            comment_id=str(comment.id),
            reports_count=comment.reports_count,
            was_escalated=was_escalated,
        )

    async def _calculate_weighted_score(self, comment: Comment) -> float:
        """
        Calculate weighted moderation score based on report reasons.
        
        Score = sum(weight * count for each reason)
        
        This determines if AI moderation pipeline should be triggered.
        Threshold: 5.0 = escalate to AI review
        """
        # Query all reports for this comment, grouped by reason
        stmt = select(Report.reason).where(Report.comment_id == comment.id)
        result = await self.db.execute(stmt)
        reasons = result.scalars().all()
        
        score = 0.0
        for reason in reasons:
            weight = REASON_WEIGHTS.get(reason, 0.5)
            score += weight
        
        return score

    async def get_report_stats(self, comment_id: str) -> dict:
        """Get report statistics for a comment (admin use)."""
        comment_uuid = uuid.UUID(str(comment_id))
        
        stmt = select(Report).where(Report.comment_id == comment_uuid)
        result = await self.db.execute(stmt)
        reports = result.scalars().all()
        
        reason_counts = {}
        for report in reports:
            reason = report.reason
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        weighted_score = await self._calculate_weighted_score(
            await self.db.get(Comment, comment_uuid)
        )
        
        return {
            "total_reports": len(reports),
            "reason_breakdown": reason_counts,
            "weighted_score": weighted_score,
            "escalated_count": sum(1 for r in reports if r.escalated),
        }

