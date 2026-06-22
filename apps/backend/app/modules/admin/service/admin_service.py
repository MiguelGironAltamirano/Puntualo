"""app/modules/admin/service/admin_service.py - Admin moderation service."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.comment import Comment, CommentStatus
from app.models.report import Report, ReportStatus
from app.models.user import User
from app.modules.evaluations.errors import CommentNotFoundError
from app.services.moderation.moderation_pipeline import ModerationPipeline
from app.utils.moderation import get_banned_terms_by_severity


class AdminService:
    """Service for admin moderation operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.moderation = ModerationPipeline(db)

    async def get_pending_moderation_comments(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Comment], int]:
        """Get comments pending moderation (hidden_pending_review status)."""
        # Count total
        count_stmt = select(func.count(Comment.id)).where(
            Comment.status == CommentStatus.HIDDEN_PENDING_REVIEW.value
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated results
        stmt = (
            select(Comment)
            .where(Comment.status == CommentStatus.HIDDEN_PENDING_REVIEW.value)
            .order_by(Comment.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        comments = result.scalars().all()

        return comments, total

    async def get_comment_detail_for_moderation(
        self,
        comment_id: str,
    ) -> dict:
        """Get detailed moderation info for a comment."""
        comment_uuid = uuid.UUID(str(comment_id))
        comment = await self.db.get(Comment, comment_uuid)
        
        if comment is None:
            raise CommentNotFoundError()

        # Get all reports for this comment
        stmt = select(Report).where(Report.comment_id == comment.id)
        result = await self.db.execute(stmt)
        reports = result.scalars().all()

        # Calculate stats
        reason_breakdown = {}
        for report in reports:
            reason = report.reason
            reason_breakdown[reason] = reason_breakdown.get(reason, 0) + 1

        weighted_score = await self._calculate_weighted_score(comment)

        return {
            "comment_id": comment.id,
            "content": comment.content,
            "status": comment.status,
            "reports_count": comment.reports_count,
            "professor_id": comment.professor_id,
            "user_id": comment.user_id,
            "created_at": comment.created_at,
            "total_reports": len(reports),
            "reason_breakdown": reason_breakdown,
            "weighted_score": weighted_score,
            "escalated_count": sum(1 for r in reports if r.escalated),
            "reports": [
                {
                    "id": r.id,
                    "comment_id": r.comment_id,
                    "user_id": r.user_id,
                    "reason": r.reason,
                    "description": r.description,
                    "escalated": r.escalated,
                    "created_at": r.created_at,
                    "updated_at": r.updated_at,
                }
                for r in reports
            ],
        }

    async def apply_moderation_decision(
        self,
        comment_id: str,
        decision: str,
        admin_notes: str | None = None,
    ) -> dict:
        """Apply admin decision (remove or allow) to a comment."""
        comment_uuid = uuid.UUID(str(comment_id))
        comment = await self.db.get(Comment, comment_uuid)
        
        if comment is None:
            raise CommentNotFoundError()

        user = await self.db.get(User, comment.user_id)
        if user is None:
            raise ValueError("User not found")

        # Apply decision
        await self.moderation.apply_admin_decision(
            comment=comment,
            user=user,
            decision=decision,
        )

        # Update report status
        stmt = select(Report).where(Report.comment_id == comment.id)
        result = await self.db.execute(stmt)
        reports = result.scalars().all()
        
        for report in reports:
            report.status = (
                ReportStatus.RESOLVED_OFFENSIVE.value
                if decision == "remove"
                else ReportStatus.RESOLVED_SAFE.value
            )

        await self.db.commit()
        await self.db.refresh(user)

        return {
            "comment_id": comment.id,
            "decision": decision,
            "user_strikes": user.strike_count or 0,
            "user_deactivated": not user.is_active,
            "admin_notes": admin_notes,
        }

    async def get_moderation_stats(self) -> dict:
        """Get system-wide moderation statistics."""
        # Comment stats
        total_comments = await self.db.execute(
            select(func.count(Comment.id))
        )
        published = await self.db.execute(
            select(func.count(Comment.id)).where(
                Comment.status == CommentStatus.PUBLISHED.value
            )
        )
        hidden_pending = await self.db.execute(
            select(func.count(Comment.id)).where(
                Comment.status == CommentStatus.HIDDEN_PENDING_REVIEW.value
            )
        )
        removed = await self.db.execute(
            select(func.count(Comment.id)).where(
                Comment.status == CommentStatus.REMOVED.value
            )
        )

        # Report stats
        total_reports = await self.db.execute(
            select(func.count(Report.id))
        )

        # User stats
        total_strikes = await self.db.execute(
            select(func.sum(User.strike_count)).where(User.strike_count > 0)
        )
        active_users = await self.db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        deactivated_by_strikes = await self.db.execute(
            select(func.count(User.id)).where(
                (User.is_active == False) & (User.strike_count >= 3)
            )
        )

        return {
            "total_comments": total_comments.scalar() or 0,
            "published": published.scalar() or 0,
            "hidden_pending_review": hidden_pending.scalar() or 0,
            "removed": removed.scalar() or 0,
            "total_reports": total_reports.scalar() or 0,
            "total_strikes_issued": total_strikes.scalar() or 0,
            "active_users": active_users.scalar() or 0,
            "deactivated_users_due_to_strikes": deactivated_by_strikes.scalar() or 0,
        }

    async def get_banned_terms_list(self) -> dict:
        """Get list of all banned terms and their severity."""
        terms_dict = {}
        
        for severity_level, terms_list in get_banned_terms_by_severity().items():
            for term in terms_list:
                terms_dict[term] = severity_level

        return {
            "terms": terms_dict,
            "count": len(terms_dict),
        }

    async def _calculate_weighted_score(self, comment: Comment) -> float:
        """Calculate weighted moderation score (same as report service)."""
        from app.modules.evaluations.service.report_service import REASON_WEIGHTS
        
        stmt = select(Report.reason).where(Report.comment_id == comment.id)
        result = await self.db.execute(stmt)
        reasons = result.scalars().all()

        score = 0.0
        for reason in reasons:
            weight = REASON_WEIGHTS.get(reason, 0.5)
            score += weight

        return score
