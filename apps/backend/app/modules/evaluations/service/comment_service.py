"""Comment service.

Lectura publica de comentarios (status='published'). Soporta:
   - filtro por professor_id (siempre)
   - filtro por course_id (AND)
   - filtro por hashtags (OR entre ellos)
   - filtro por modality
   - filtro por rango de likes/dislikes
   - búsqueda full-text en texto del comentario
   - filtro por fecha de creación
   - sort: recent (default, created_at DESC) | likes (like_count DESC, created_at DESC)
"""
from datetime import datetime
from typing import Iterable, Literal

from sqlalchemy import Select, and_, exists, func, select
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
        search: str | None = None,
        min_likes: int | None = None,
        max_likes: int | None = None,
        min_dislikes: int | None = None,
        max_dislikes: int | None = None,
        min_net_score: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        exclude_offensive: bool = False,
    ) -> Select[tuple[Comment]]:
        base = select(Comment).where(
            Comment.professor_id == professor_id,
            Comment.status == CommentStatus.PUBLISHED.value,
        )
        
        if course_id is not None:
            base = base.where(Comment.course_id == course_id)
        
        if modality is not None:
            base = base.where(Comment.modality == modality)

        # Hashtag filtering (OR logic)
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

        # Text search (only if comment text is not null/removed)
        if search:
            term = f"%{search.strip().lower()}%"
            base = base.where(
                Comment.text.isnot(None),
                func.lower(Comment.text).like(term)
            )

        # Like/Dislike filters
        if min_likes is not None:
            base = base.where(Comment.like_count >= min_likes)
        if max_likes is not None:
            base = base.where(Comment.like_count <= max_likes)
        
        if min_dislikes is not None:
            base = base.where(Comment.dislike_count >= min_dislikes)
        if max_dislikes is not None:
            base = base.where(Comment.dislike_count <= max_dislikes)
        
        # Net score (likes - dislikes)
        if min_net_score is not None:
            base = base.where(
                (Comment.like_count - Comment.dislike_count) >= min_net_score
            )

        # Date range filters
        if date_from:
            try:
                from_date = datetime.fromisoformat(date_from)
                base = base.where(Comment.created_at >= from_date)
            except (ValueError, TypeError):
                pass  # Ignore invalid dates
        
        if date_to:
            try:
                to_date = datetime.fromisoformat(date_to)
                base = base.where(Comment.created_at <= to_date)
            except (ValueError, TypeError):
                pass  # Ignore invalid dates

        # Exclude offensive/removed comments
        if exclude_offensive:
            base = base.where(Comment.moderation_verdict != "remove")

        # Apply sorting
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
