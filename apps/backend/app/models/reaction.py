import enum
import uuid

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ReactionType(str, enum.Enum):
    LIKE = "like"
    DISLIKE = "dislike"


class Reaction(Base, TimestampMixin):
    """
    Una reacción por (comment, user). Tipos: like / dislike.
    El campo type se guarda como String en DB para permitir ampliar el catálogo
    relajando el CHECK constraint sin migrar datos.
    """

    __tablename__ = "comment_reactions"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    comment_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type: Mapped[str] = mapped_column(String(20), nullable=False)

    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", name="uq_reactions_user_comment"),
        CheckConstraint("type IN ('like','dislike')", name="ck_reactions_type"),
    )
