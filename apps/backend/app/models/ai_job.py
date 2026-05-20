import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AiJob(Base):
    """
    Cola de estado de tareas asíncronas de IA procesadas por workers Celery.
    job_type describe la operación (summary_generation, content_moderation, etc.).
    Los workers leen filas 'pending', actualizan a 'running' y finalizan en
    'completed' o 'failed'.
    """

    __tablename__ = "ai_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    job_type: Mapped[str] = mapped_column(String(100), nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
    )

    input_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    result_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','running','completed','failed')",
            name="ck_ai_jobs_status",
        ),
    )
