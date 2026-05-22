"""Comment service.

Lectura publica de comentarios (status='published'). Soporta:
  - filtro por professor_id (siempre)
  - filtro por course_id (AND)
  - filtro por hashtags (OR entre ellos)
  - filtro por modality
  - sort: recent (default, created_at DESC) | likes (like_count DESC, created_at DESC)
"""
from typing import Iterable, Literal

from sqlalchemy import Select, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment, CommentStatus
from app.models.evaluation_hashtag import EvaluationHashtag
from app.models.hashtag import Hashtag

SortBy = Literal["recent", "likes"]
ModalityFilter = Literal["virtual", "presencial", "ambas"]


class CommentService:

    def __init__(self, db: AsyncSession):
        self.db = db

    def list_query(
        self,
        *,
        professor_id: str,
        sort_by: SortBy = "recent",
        course_id: int | None = None,
        hashtags: Iterable[str] | None = None,
        modality: ModalityFilter | None = None,
    ) -> Select[tuple[Comment]]:
        base = select(Comment).where(
            Comment.professor_id == professor_id,
            Comment.status == CommentStatus.PUBLISHED.value,
        )
        if course_id is not None:
            base = base.where(Comment.course_id == course_id)
        if modality is not None:
            base = base.where(Comment.modality == modality)

        hashtag_list = [h.lower() for h in (hashtags or []) if h]
        if hashtag_list:
            # OR entre hashtags: existe AL MENOS UNO de ellos atado a la evaluation del comment.
            subq = (
                select(1)
                .select_from(EvaluationHashtag)
                .join(Hashtag, Hashtag.id == EvaluationHashtag.hashtag_id)
                .where(
                    EvaluationHashtag.evaluation_id == Comment.evaluation_id,
                    Hashtag.label.in_(hashtag_list),
                )
            )
            base = base.where(exists(subq))

        if sort_by == "likes":
            return base.order_by(Comment.like_count.desc(), Comment.created_at.desc())
        # default: recent
        return base.order_by(Comment.created_at.desc())

    async def get_by_id(self, comment_id: str) -> Comment | None:
        stmt = select(Comment).where(
            Comment.id == comment_id,
            Comment.status == CommentStatus.PUBLISHED.value,
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()
