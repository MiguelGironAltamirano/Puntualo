import enum
import uuid

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ReactionType(str, enum.Enum):
    """
    Tipos de reacción soportados en MVP. Diseñado para crecer a más tipos
    (emojis) sin tocar el código del service:

      1. Ampliar este enum (o ignorarlo si se usa String libre).
      2. Relajar el CHECK constraint en DB (`ALTER TABLE ... DROP CONSTRAINT`
         y recrearlo con la lista nueva).
      3. Ampliar la allowlist en `settings.REACTION_ALLOWED_TYPES`.
      4. Reemplazar los counters fijos `helpful_count` / `not_helpful_count`
         del modelo `Comment` por un agregado dinámico.
    """

    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"


class Reaction(Base, TimestampMixin):
    """
    Una reacción por (comment, user). El campo `type` se guarda como String(20)
    en DB (no enum estricto) para permitir extender el catálogo sin migraciones
    de schema, solo relajando el CHECK constraint. Ver docstring de `ReactionType`.
    """

    __tablename__ = "comment_reactions"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    comment_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "comment_id",
            "user_id",
            name="uq_reactions_user_comment",
        ),
        CheckConstraint(
            "type IN ('helpful','not_helpful')",
            name="ck_reactions_type",
        ),
    )
