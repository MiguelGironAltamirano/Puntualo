"""app/modules/admin/router/admin_router.py - Admin moderation API endpoints."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.async_session import get_async_db
from app.modules.admin.schemas.index import (
    BannedTermsListResponse,
    CommentModerationDetail,
    ModerationActionResponse,
    ModerationDecisionRequest,
    ModerationStatsResponse,
    ReportListResponse,
    ReportSummary,
    UserAdminRead,
    UserAdminListResponse,
    UserReportItem,
    UserReportsListResponse,
)
from app.modules.admin.service.admin_service import AdminService
from app.modules.auth.dependencies import get_current_user
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/api/admin", tags=["admin"])


async def get_admin_service(
    db: Annotated[AsyncSession, Depends(get_async_db)],
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
    admin_notes = request.admin_notes or request.reason
    result = await service.apply_moderation_decision(
        comment_id=comment_id,
        decision=request.decision,
        admin_notes=admin_notes,
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


@router.get(
    "/users",
    response_model=UserAdminListResponse,
    dependencies=[Depends(require_admin)],
)
async def list_users(
    service: Annotated[AdminService, Depends(get_admin_service)],
    search: str | None = Query(None),
    role: str | None = Query(None),
    is_active: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all registered users (admin only)."""
    users, total = await service.get_users_list(
        search=search,
        role=role,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )
    pages = (total + page_size - 1) // page_size
    return UserAdminListResponse(
        items=[UserAdminRead.model_validate(u) for u in users],
        total=total,
        page=page,
        pages=pages,
    )


@router.post(
    "/users/{user_id}/ban",
    response_model=UserAdminRead,
    dependencies=[Depends(require_admin)],
)
async def ban_user(
    user_id: str,
    service: Annotated[AdminService, Depends(get_admin_service)],
):
    """Deactivate/Ban a user account (admin only)."""
    try:
        user = await service.ban_user(user_id)
        return UserAdminRead.model_validate(user)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "/users/{user_id}/unban",
    response_model=UserAdminRead,
    dependencies=[Depends(require_admin)],
)
async def unban_user(
    user_id: str,
    service: Annotated[AdminService, Depends(get_admin_service)],
):
    """Reactivate/Unban a user account and reset strike count (admin only)."""
    try:
        user = await service.unban_user(user_id)
        return UserAdminRead.model_validate(user)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/users/{user_id}/reports",
    response_model=UserReportsListResponse,
    dependencies=[Depends(require_admin)],
)
async def get_user_reports(
    user_id: str,
    service: Annotated[AdminService, Depends(get_admin_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Get list of reports against a user's comments (admin only)."""
    reports_data, total = await service.get_user_reports(
        user_id=user_id,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size
    return UserReportsListResponse(
        items=[UserReportItem(**item) for item in reports_data],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


