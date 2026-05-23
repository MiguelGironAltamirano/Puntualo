"""app/modules/evaluations/routers/reactions.py"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.async_session import get_async_db
from app.models.user import User
from app.modules.auth.dependencies import get_current_user
from app.modules.evaluations.errors import CommentNotFoundError
from app.modules.evaluations.schemas import ReactionCreate, ReactionResult
from app.modules.evaluations.service.reaction_service import ReactionService
from app.schemas.error import ErrorResponse

router = APIRouter()


@router.post(
    "/comments/{comment_id}/reactions",
    response_model=ReactionResult,
    summary="Toggle like/dislike sobre un comentario",
    responses={
        401: {"model": ErrorResponse, "description": "No autenticado"},
        404: {"model": ErrorResponse, "description": "Comentario no encontrado"},
    },
)
async def toggle_reaction(
    comment_id: str,
    payload: ReactionCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> ReactionResult:
    svc = ReactionService(db)
    try:
        result = await svc.toggle(
            comment_id=comment_id,
            user_id=current_user.id,
            reaction_type=payload.type,
        )
    except CommentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": exc.code, "message": str(exc)},
        )
    return ReactionResult(
        comment_id=result.comment_id,
        user_reaction=result.user_reaction,
        like_count=result.like_count,
        dislike_count=result.dislike_count,
    )
