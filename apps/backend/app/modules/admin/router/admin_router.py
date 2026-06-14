"""app/modules/admin/router/admin_router.py - Admin moderation API endpoints."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.session import get_db
from app.modules.admin.schemas.index import (
    BannedTermsListResponse,
    CommentModerationDetail,
    ModerationActionResponse,
    ModerationDecisionRequest,
    ModerationStatsResponse,
    ReportListResponse,
    ReportSummary,
)
from app.modules.admin.service.admin_service import AdminService
from app.modules.auth.dependencies import get_current_user
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/api/admin", tags=["admin"])


async def get_admin_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AdminService:
    """Dependency: AdminService."""
    return AdminService(db)


async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require current user to be admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get(
    "/moderation/pending",
    response_model=list[CommentModerationDetail],
    dependencies=[Depends(require_admin)],
)
async def get_pending_moderation(
    service: Annotated[AdminService, Depends(get_admin_service)],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get comments pending moderation (admin only)."""
    comments, _ = await service.get_pending_moderation_comments(
        limit=limit, offset=offset
    )
    
    results = []
    for comment in comments:
        detail = await service.get_comment_detail_for_moderation(str(comment.id))
        results.append(CommentModerationDetail(**detail))
    
    return results


@router.get(
    "/moderation/comments/{comment_id}",
    response_model=CommentModerationDetail,
    dependencies=[Depends(require_admin)],
)
async def get_comment_detail(
    comment_id: str,
    service: Annotated[AdminService, Depends(get_admin_service)],
):
    """Get detailed moderation info for a comment."""
    detail = await service.get_comment_detail_for_moderation(comment_id)
    return CommentModerationDetail(**detail)


@router.post(
    "/moderation/comments/{comment_id}/decide",
    response_model=ModerationActionResponse,
    dependencies=[Depends(require_admin)],
)
async def apply_moderation_decision(
    comment_id: str,
    request: ModerationDecisionRequest,
    service: Annotated[AdminService, Depends(get_admin_service)],
):
    """Apply admin moderation decision (remove or allow)."""
    result = await service.apply_moderation_decision(
        comment_id=comment_id,
        decision=request.decision,
        admin_notes=request.admin_notes,
    )
    return ModerationActionResponse(**result)


@router.get(
    "/moderation/stats",
    response_model=ModerationStatsResponse,
    dependencies=[Depends(require_admin)],
)
async def get_moderation_stats(
    service: Annotated[AdminService, Depends(get_admin_service)],
):
    """Get system-wide moderation statistics."""
    stats = await service.get_moderation_stats()
    return ModerationStatsResponse(**stats)


@router.get(
    "/moderation/banned-terms",
    response_model=BannedTermsListResponse,
    dependencies=[Depends(require_admin)],
)
async def get_banned_terms(
    service: Annotated[AdminService, Depends(get_admin_service)],
):
    """Get list of banned terms and severity levels."""
    result = await service.get_banned_terms_list()
    return BannedTermsListResponse(**result)
