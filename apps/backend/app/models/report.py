import enum
import uuid

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ReportReason(str, enum.Enum):
    SPAM = "spam"
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    OFF_TOPIC = "off_topic"
    OTHER = "other"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    RESOLVED_OFFENSIVE = "resolved_offensive"
    RESOLVED_SAFE = "resolved_safe"


class Report(Base, TimestampMixin):
    """
    Denuncia (1 por user, 1 por comment, idempotente vía UNIQUE). Al cruzar
    5 denuncias, el pipeline de IA se activa para decidir mantener o eliminar
    el comentario.
    """

    __tablename__ = "comment_reports"

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

    reason: Mapped[str] = mapped_column(String(20), nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=ReportStatus.PENDING.value,
    )

    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", name="uq_reports_user_comment"),
        CheckConstraint(
            "reason IN ('spam','hate_speech','harassment','off_topic','other')",
            name="ck_reports_reason",
        ),
        CheckConstraint(
            "status IN ('pending','under_review','resolved_offensive','resolved_safe')",
            name="ck_reports_status",
        ),
    )
