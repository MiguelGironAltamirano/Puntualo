"""app/modules/evaluations/service/report_service.py"""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment, CommentStatus
from app.models.report import Report
from app.modules.evaluations.errors import (
    CommentNotFoundError,
    ReportDuplicateError,
)


@dataclass
class ReportResult:
    comment_id: str
    reports_count: int


class ReportService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        comment_id: str,
        user_id: uuid.UUID,
        reason: str,
        description: str | None,
    ) -> ReportResult:
        comment = await self.db.get(Comment, uuid.UUID(str(comment_id)))
        if comment is None or comment.status != CommentStatus.PUBLISHED.value:
            raise CommentNotFoundError()

        report = Report(
            comment_id=comment.id,
            user_id=user_id,
            reason=reason,
            description=description,
        )
        self.db.add(report)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            await self.db.rollback()
            raise ReportDuplicateError() from exc

        comment.reports_count += 1
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(comment)
        return ReportResult(
            comment_id=str(comment.id),
            reports_count=comment.reports_count,
        )
