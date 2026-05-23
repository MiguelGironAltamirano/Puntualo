"""app/modules/evaluations/routers/comments.py

Endpoints publicos (anonimato garantizado RF-18):
  GET /professors/{professor_id}/comments?course_id=...&hashtags=...&order_by=...&page=...
  GET /comments/{comment_id}
"""
from __future__ import annotations

from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.async_session import get_async_db
from app.models.evaluation_hashtag import EvaluationHashtag
from app.models.hashtag import Hashtag
from app.modules.evaluations.schemas import CommentRead
from app.modules.evaluations.service.comment_service import CommentService, SortBy
from app.schemas.error import ErrorResponse

router = APIRouter()

MAX_PAGE_SIZE = 50


@router.get(
    "/professors/{professor_id}/comments",
    summary="Listar comentarios publicos de un profesor (anonimo, filtrable, paginado)",
)
async def list_professor_comments(
    professor_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=MAX_PAGE_SIZE),
    course_id: int | None = Query(default=None, gt=0),
    hashtags: list[str] | None = Query(default=None),
    order_by: SortBy = Query("recent"),
    db: AsyncSession = Depends(get_async_db),
):
    svc = CommentService(db)
    base = svc.list_query(
        professor_id=professor_id,
        sort_by=order_by,
        course_id=course_id,
        hashtags=hashtags,
    )
    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    page_stmt = base.offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(page_stmt)).scalars().all())

    # Cargar hashtags por comment.evaluation_id en una sola query.
    eval_ids = [c.evaluation_id for c in items]
    hashtag_map: dict = {eid: [] for eid in eval_ids}
    if eval_ids:
        h_stmt = (
            select(EvaluationHashtag.evaluation_id, Hashtag.label)
            .join(Hashtag, Hashtag.id == EvaluationHashtag.hashtag_id)
            .where(EvaluationHashtag.evaluation_id.in_(eval_ids))
        )
        for row in (await db.execute(h_stmt)).all():
            hashtag_map.setdefault(row.evaluation_id, []).append(row.label)

    total_pages = ceil(total / page_size) if total > 0 else 0
    return {
        "items": [
            CommentRead(
                id=str(c.id),
                professor_id=str(c.professor_id),
                course_id=c.course_id,
                text=c.text,
                modality=c.modality,
                like_count=c.like_count,
                dislike_count=c.dislike_count,
                created_at=c.created_at,
                hashtags=hashtag_map.get(c.evaluation_id, []),
            ).model_dump()
            for c in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


@router.get(
    "/comments/{comment_id}",
    response_model=CommentRead,
    summary="Obtener un comentario publicado por ID (anonimo)",
    responses={404: {"model": ErrorResponse, "description": "Comentario no encontrado o no publicado"}},
)
async def get_comment(
    comment_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    svc = CommentService(db)
    comment = await svc.get_by_id(comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "COMMENT_NOT_FOUND", "message": "Comentario no encontrado"},
        )
    # Hashtags
    h_stmt = (
        select(Hashtag.label)
        .join(EvaluationHashtag, EvaluationHashtag.hashtag_id == Hashtag.id)
        .where(EvaluationHashtag.evaluation_id == comment.evaluation_id)
    )
    labels = [r[0] for r in (await db.execute(h_stmt)).all()]
    return CommentRead(
        id=str(comment.id),
        professor_id=str(comment.professor_id),
        course_id=comment.course_id,
        text=comment.text,
        modality=comment.modality,
        like_count=comment.like_count,
        dislike_count=comment.dislike_count,
        created_at=comment.created_at,
        hashtags=labels,
    )
