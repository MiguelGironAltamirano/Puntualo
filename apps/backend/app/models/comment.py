import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class CommentStatus(str, enum.Enum):
    PUBLISHED = "published"
    HIDDEN_PENDING_REVIEW = "hidden_pending_review"
    REMOVED = "removed"


class Comment(Base, TimestampMixin, SoftDeleteMixin):
    """
    Un comentario por evaluación (UNIQUE evaluation_id). Denormaliza professor_id
    y course_id para filtros y listados rápidos.

    Counters fijos `helpful_count` / `not_helpful_count` cubren los 2 tipos de
    Reaction del MVP. Cuando se agreguen más tipos (emojis), reemplazar por
    agregado dinámico (`reactions_summary: JSONB` o tabla `comment_reaction_summary`).
    """

    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    evaluation_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("evaluations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    user_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    professor_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("professors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    course_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("courses.id", ondelete="RESTRICT"),
        nullable=False,
    )

    text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )

    modality: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=CommentStatus.PUBLISHED.value,
        index=True,
    )

    hidden_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    removed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    moderation_verdict: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        default=None,
    )

    helpful_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    not_helpful_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    reports_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    __table_args__ = (
        Index("ix_comments_professor_status", "professor_id", "status"),
        CheckConstraint(
            "status IN ('published','hidden_pending_review','removed')",
            name="ck_comments_status",
        ),
        CheckConstraint(
            "modality IN ('virtual','presencial','ambas')",
            name="ck_comments_modality",
        ),
        CheckConstraint(
            "(removed_at IS NULL) OR (text IS NULL)",
            name="ck_comments_text_null_when_removed",
        ),
    )
