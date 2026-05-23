"""app/modules/evaluations/service/reaction_service.py

Toggle de reacciones like/dislike sobre comentarios.

Reglas:
  - usuario sin reaccion previa + click `like`     -> INSERT like   (like_count +1)
  - usuario con reaccion `like` + click `like`     -> DELETE         (like_count -1)
  - usuario con reaccion `like` + click `dislike`  -> UPDATE         (like_count -1, dislike_count +1)
  - mismo simetrico para dislike.

Self-reaction: permitida (cualquier user puede reaccionar 1 vez por comment,
incluso el autor). UNIQUE(comment_id, user_id) garantiza la unicidad.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment, CommentStatus
from app.models.reaction import Reaction
from app.modules.evaluations.errors import CommentNotFoundError

ReactionType = Literal["like", "dislike"]


@dataclass
class ToggleResult:
    comment_id: str
    user_reaction: ReactionType | None
    like_count: int
    dislike_count: int


class ReactionService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def toggle(
        self,
        *,
        comment_id: str,
        user_id: uuid.UUID,
        reaction_type: ReactionType,
    ) -> ToggleResult:
        comment = await self.db.get(Comment, comment_id)
        if comment is None or comment.status != CommentStatus.PUBLISHED.value:
            raise CommentNotFoundError()

        stmt = select(Reaction).where(
            Reaction.comment_id == comment_id,
            Reaction.user_id == user_id,
        )
        existing = (await self.db.execute(stmt)).scalar_one_or_none()

        if existing is None:
            # INSERT
            self.db.add(Reaction(comment_id=comment_id, user_id=user_id, type=reaction_type))
            if reaction_type == "like":
                comment.like_count += 1
            else:
                comment.dislike_count += 1
            final = reaction_type
        elif existing.type == reaction_type:
            # TOGGLE OFF (DELETE)
            await self.db.delete(existing)
            if reaction_type == "like":
                comment.like_count = max(0, comment.like_count - 1)
            else:
                comment.dislike_count = max(0, comment.dislike_count - 1)
            final = None
        else:
            # SWITCH
            if existing.type == "like":
                comment.like_count = max(0, comment.like_count - 1)
                comment.dislike_count += 1
            else:
                comment.dislike_count = max(0, comment.dislike_count - 1)
                comment.like_count += 1
            existing.type = reaction_type
            final = reaction_type

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(comment)

        return ToggleResult(
            comment_id=str(comment.id),
            user_reaction=final,
            like_count=comment.like_count,
            dislike_count=comment.dislike_count,
        )
