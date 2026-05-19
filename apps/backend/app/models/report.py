import enum
import uuid

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
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
    `MODERATION_HIDE_THRESHOLD` denuncias, el comment pasa a `hidden_pending_review`
    y los reports pendientes pasan a `under_review`.
    """

    __tablename__ = "comment_reports"

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

    reason: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=ReportStatus.PENDING.value,
    )

    __table_args__ = (
        UniqueConstraint(
            "comment_id",
            "user_id",
            name="uq_reports_user_comment",
        ),
        CheckConstraint(
            "reason IN ('spam','hate_speech','harassment','off_topic','other')",
            name="ck_reports_reason",
        ),
        CheckConstraint(
            "status IN ('pending','under_review','resolved_offensive','resolved_safe')",
            name="ck_reports_status",
        ),
    )
