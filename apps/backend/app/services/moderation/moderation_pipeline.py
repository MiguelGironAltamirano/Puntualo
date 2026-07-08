"""app/services/moderation/moderation_pipeline.py - Orchestrate heuristic + AI moderation."""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.comment import Comment, CommentStatus
from app.models.user import User
from app.models.report import Report
from app.utils.moderation import heuristic_filter


logger = logging.getLogger(__name__)


class ModerationDecision(str, Enum):
    """Final moderation decision."""
    ALLOW = "allow"
    REMOVE = "remove"
    FLAG_FOR_REVIEW = "flag_for_review"


@dataclass
class ModerationResult:
    """Result of moderation pipeline."""
    decision: ModerationDecision
    reason: str
    heuristic_score: float
    heuristic_action: str
    ai_triggered: bool = False
    ai_decision: str | None = None


class ModerationPipeline:
    """
    Orchestrates comment moderation pipeline:
    1. Heuristic filter (regex, spam detection, obfuscation)
    2. Report-triggered AI review (if 5+ weighted reports)
    3. Strike system (3 strikes = deactivation)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def moderate_comment(
        self,
        comment: Comment,
        user: User,
    ) -> ModerationResult:
        """
        Run full moderation pipeline on a comment.
        
        Returns:
            ModerationResult with decision (allow/remove/flag_for_review)
        """
        logger.info(
            f"moderation.moderate_comment | comment_id={comment.id} user_id={user.id}"
        )

        # Step 1: Heuristic filter
        heuristic_result = await heuristic_filter(comment.content, db=self.db)
        logger.info(
            f"moderation.heuristic_filter | comment_id={comment.id} "
            f"action={heuristic_result.action} spam_score={heuristic_result.spam_score}"
        )

        # Step 2: Immediate block if heuristic says block
        if heuristic_result.action == "block":
            await self._apply_moderation_verdict(
                comment=comment,
                user=user,
                decision=ModerationDecision.REMOVE,
                reason=f"Blocked by heuristic: {heuristic_result.reasons}",
            )
            return ModerationResult(
                decision=ModerationDecision.REMOVE,
                reason=f"Heuristic detection: {', '.join(heuristic_result.reasons)}",
                heuristic_score=heuristic_result.spam_score,
                heuristic_action=heuristic_result.action,
            )

        # Step 3: If heuristic flags, hide pending review
        if heuristic_result.action == "flag":
            comment.status = CommentStatus.HIDDEN_PENDING_REVIEW.value
            await self.db.flush()
            logger.info(
                f"moderation.flagged_by_heuristic | comment_id={comment.id} "
                f"reasons={heuristic_result.reasons}"
            )
            return ModerationResult(
                decision=ModerationDecision.FLAG_FOR_REVIEW,
                reason=f"Flagged by heuristic: {heuristic_result.reasons}",
                heuristic_score=heuristic_result.spam_score,
                heuristic_action=heuristic_result.action,
            )

        # Step 4: Heuristic allows — return allow
        return ModerationResult(
            decision=ModerationDecision.ALLOW,
            reason="Passed heuristic filter",
            heuristic_score=heuristic_result.spam_score,
            heuristic_action=heuristic_result.action,
        )

    async def moderate_comment_on_report_escalation(
        self,
        comment: Comment,
        user: User,
    ) -> ModerationResult:
        """
        Run moderation when a comment reaches escalation threshold via reports.
        
        This is called when weighted report score >= 5.0.
        Currently delegates to Gemini AI (if enabled), otherwise marks for manual review.
        
        Returns:
            ModerationResult with AI decision (remove/allow/flag)
        """
        logger.info(
            f"moderation.report_escalation | comment_id={comment.id} "
            f"user_id={user.id}"
        )

        # For now, mark as pending review and let AI/admin handle it
        # Future: Call Gemini API if LLM_MODERATION_ENABLED
        comment.status = CommentStatus.HIDDEN_PENDING_REVIEW.value
        await self.db.flush()

        return ModerationResult(
            decision=ModerationDecision.FLAG_FOR_REVIEW,
            reason="Escalated due to high report count",
            heuristic_score=0.0,
            heuristic_action="escalated",
            ai_triggered=False,
        )

    async def apply_admin_decision(
        self,
        comment: Comment,
        user: User,
        decision: str,  # "remove" or "allow"
    ) -> None:
        """
        Apply admin moderation decision (remove or allow comment).
        Handles strike system: 3 strikes = user deactivation.
        """
        if decision == "remove":
            comment.status = CommentStatus.REMOVED.value
            comment.moderation_verdict = "removed_by_admin"
            
            # Increment user strike
            user.strike_count = (user.strike_count or 0) + 1
            
            logger.info(
                f"moderation.admin_remove | comment_id={comment.id} "
                f"user_id={user.id} strike_count={user.strike_count}"
            )

            # 3 strikes = deactivate
            if user.strike_count >= 3:
                user.is_active = False
                logger.warning(
                    f"moderation.user_deactivated | user_id={user.id} "
                    f"strike_count={user.strike_count}"
                )

        elif decision == "allow":
            comment.status = CommentStatus.PUBLISHED.value
            comment.moderation_verdict = "allowed_by_admin"
            logger.info(
                f"moderation.admin_allow | comment_id={comment.id} "
                f"user_id={user.id}"
            )

        await self.db.flush()

    async def _apply_moderation_verdict(
        self,
        comment: Comment,
        user: User,
        decision: ModerationDecision,
        reason: str,
    ) -> None:
        """Apply internal moderation verdict to comment."""
        if decision == ModerationDecision.REMOVE:
            comment.status = CommentStatus.REMOVED.value
            comment.moderation_verdict = reason
            user.strike_count = (user.strike_count or 0) + 1

            if user.strike_count >= 3:
                user.is_active = False


class ModerationCheckpoint:
    """
    Checkpoint for moderation decisions (used in evaluation_service).
    Determines if heuristic filter should block comment on creation.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_on_comment_creation(self, content: str) -> tuple[bool, str | None]:
        """
        Check heuristic filter on comment creation.
        
        Returns:
            (should_block: bool, reason: str | None)
        """
        heuristic_result = await heuristic_filter(content, db=self.db)
        
        if heuristic_result.action == "block":
            return True, f"Blocked: {', '.join(heuristic_result.reasons)}"
        elif heuristic_result.action == "flag":
            return False, None  # Allow creation but set status to pending review in service
        
        return False, None
