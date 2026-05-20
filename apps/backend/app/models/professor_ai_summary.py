import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ProfessorAiSummary(Base, TimestampMixin):
    """
    Resumen ejecutivo generado por NLP en background para cada docente.
    Se regenera asincrónicamente cuando el volumen de nuevas reseñas supera
    un umbral. Una sola fila activa por profesor (UNIQUE professor_id).
    """

    __tablename__ = "professor_ai_summaries"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    professor_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("professors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    summary: Mapped[str] = mapped_column(Text, nullable=False)

    pros: Mapped[list] = mapped_column(
        ARRAY(Text),
        nullable=False,
        server_default=text("'{}'::text[]"),
    )

    cons: Mapped[list] = mapped_column(
        ARRAY(Text),
        nullable=False,
        server_default=text("'{}'::text[]"),
    )

    model_version: Mapped[str] = mapped_column(String(100), nullable=False)

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("professor_id", name="uq_professor_ai_summaries_professor"),
    )
