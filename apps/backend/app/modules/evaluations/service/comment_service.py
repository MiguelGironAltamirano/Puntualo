"""Comment service — Tarea 7 (lectura publica).

Endpoints publicos (sin JWT) sirven solo comentarios `status='published'`.
Sirven dos shapes:
  - listado por profesor con sort/filtros
  - get individual (404 si esta hidden/removed)
"""
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment, CommentStatus

SortBy = Literal["recent", "helpful"]
ModalityFilter = Literal["virtual", "presencial", "ambas"]


class CommentService:

    def __init__(self, db: AsyncSession):
        self.db = db

    def list_query(
        self,
        *,
        professor_id: str,
        sort_by: SortBy = "recent",
        modality: ModalityFilter | None = None,
        is_verified_only: bool = False,
    ):
        """Query base de comentarios publicados de un profesor.

        Se pasa al helper `paginate` desde el router (Tarea 12). Siempre filtra
        `status='published'` — nunca expone hidden/removed en lectura publica.
        """
        base = select(Comment).where(
            Comment.professor_id == professor_id,
            Comment.status == CommentStatus.PUBLISHED.value,
        )
        if modality is not None:
            base = base.where(Comment.modality == modality)
        if is_verified_only:
            base = base.where(Comment.is_verified.is_(True))

        if sort_by == "helpful":
            net_helpful = Comment.helpful_count - Comment.not_helpful_count
            return base.order_by(
                net_helpful.desc(),
                Comment.helpful_count.desc(),
                Comment.created_at.desc(),
            )
        # default: "recent"
        return base.order_by(Comment.created_at.desc())

    async def get_by_id(self, comment_id: str) -> Comment | None:
        """Devuelve el comment solo si `status='published'`. Si no, None (router -> 404)."""
        stmt = select(Comment).where(
            Comment.id == comment_id,
            Comment.status == CommentStatus.PUBLISHED.value,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
