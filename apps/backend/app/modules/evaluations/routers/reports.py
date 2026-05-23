"""app/modules/evaluations/routers/reports.py"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.async_session import get_async_db
from app.models.user import User
from app.modules.auth.dependencies import get_current_user
from app.modules.evaluations.errors import (
    CommentNotFoundError,
    ReportDuplicateError,
)
from app.modules.evaluations.schemas import ReportCreate, ReportResult
from app.modules.evaluations.service.report_service import ReportService
from app.schemas.error import ErrorResponse

router = APIRouter()


@router.post(
    "/comments/{comment_id}/reports",
    response_model=ReportResult,
    status_code=status.HTTP_201_CREATED,
    summary="Denunciar comentario (un report por user/comment)",
    responses={
        401: {"model": ErrorResponse, "description": "No autenticado"},
        404: {"model": ErrorResponse, "description": "Comentario no encontrado"},
        409: {"model": ErrorResponse, "description": "Denuncia duplicada"},
    },
)
async def create_report(
    comment_id: str,
    payload: ReportCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> ReportResult:
    svc = ReportService(db)
    try:
        result = await svc.create(
            comment_id=comment_id,
            user_id=current_user.id,
            reason=payload.reason,
            description=payload.description,
        )
    except CommentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": exc.code, "message": str(exc)},
        )
    except ReportDuplicateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": exc.code, "message": str(exc)},
        )
    return ReportResult(
        comment_id=result.comment_id,
        reports_count=result.reports_count,
    )
