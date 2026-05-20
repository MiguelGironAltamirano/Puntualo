import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class CommentStatus(str, enum.Enum):
    PUBLISHED = "published"
    HIDDEN_PENDING_REVIEW = "hidden_pending_review"
    REMOVED = "removed"


class Comment(Base, TimestampMixin, SoftDeleteMixin):
    """
    Texto anónimo vinculado 1:1 a una evaluación. Todos los comentarios son
    anónimos en la API pública; user_id se almacena internamente para el sistema
    de strikes y el pipeline de moderación por IA.

    Contadores denormalizados like_count / dislike_count / reports_count para
    rendimiento en listados. Se actualizan en la capa de servicio al registrar
    reacciones o denuncias.
    """

    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("evaluations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    professor_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("professors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    course_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("courses.id", ondelete="RESTRICT"),
        nullable=False,
    )

    text: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    modality: Mapped[str] = mapped_column(String(15), nullable=False)

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=CommentStatus.PUBLISHED.value,
        index=True,
    )

    hidden_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    removed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    moderation_verdict: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)

    like_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dislike_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reports_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

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
