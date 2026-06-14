"""app/modules/admin/schemas/index.py - Admin API schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReportSummary(BaseModel):
    """Summary of a single report."""
    id: UUID
    comment_id: UUID
    user_id: UUID
    reason: str
    description: str | None
    escalated: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentModerationDetail(BaseModel):
    """Detailed info about a comment pending moderation."""
    comment_id: UUID
    content: str
    status: str
    reports_count: int
    professor_id: UUID
    user_id: UUID
    created_at: datetime
    total_reports: int
    reason_breakdown: dict[str, int]
    weighted_score: float
    escalated_count: int
    reports: list[ReportSummary]

    class Config:
        from_attributes = True


class ModerationDecisionRequest(BaseModel):
    """Request to apply admin moderation decision."""
    decision: str = Field(..., pattern="^(remove|allow)$")
    admin_notes: str | None = None


class ModerationActionResponse(BaseModel):
    """Response after applying moderation decision."""
    comment_id: UUID
    decision: str
    user_strikes: int
    user_deactivated: bool
    admin_notes: str | None = None


class ReportListResponse(BaseModel):
    """List of reports pending moderation."""
    total: int
    pending: int
    under_review: int
    reports: list[ReportSummary]


class BannedTermsListResponse(BaseModel):
    """List of banned terms and their severity."""
    terms: dict[str, str]  # term -> severity (low/medium/high)
    count: int


class ModerationStatsResponse(BaseModel):
    """System-wide moderation statistics."""
    total_comments: int
    published: int
    hidden_pending_review: int
    removed: int
    total_reports: int
    total_strikes_issued: int
    active_users: int
    deactivated_users_due_to_strikes: int
