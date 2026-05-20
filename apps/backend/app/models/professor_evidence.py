import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ProfessorEvidence(Base, TimestampMixin):
    """
    Una fila por (professor, source). Guarda el payload raw para auditoría,
    debugging, y como input al resumen IA (Fase 4).
    """

    __tablename__ = "professor_evidence"

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

    source: Mapped[str] = mapped_column(String(30), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    found: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    affiliation_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    confidence: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)

    raw_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    fetched_at: Mapped[datetime] = mapped_column(
        "fetched_at",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_professor_evidence_lookup", "professor_id", "source"),
    )
