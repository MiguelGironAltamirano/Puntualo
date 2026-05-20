import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ModerationAction(Base, TimestampMixin):
    """
    Decisión tomada por el pipeline de IA cuando un comentario acumula 5
    denuncias. Registra la decisión, la justificación del modelo y el contexto
    del trigger para auditoría.
    """

    __tablename__ = "moderation_actions"

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

    decision: Mapped[str] = mapped_column("decision", nullable=False)

    reasoning: Mapped[str] = mapped_column(Text, nullable=False)

    reports_count_at_trigger: Mapped[int] = mapped_column(Integer, nullable=False)

    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "decision IN ('keep','remove')",
            name="ck_moderation_actions_decision",
        ),
    )
