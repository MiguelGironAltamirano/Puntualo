import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class VerificationRequest(Base, TimestampMixin):

    __tablename__ = "verification_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    document_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("uploaded_documents.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )

    status: Mapped[str] = mapped_column(
        "status",
        nullable=False,
        default="pending",
    )

    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','approved','rejected')",
            name="ck_verification_requests_status",
        ),
    )
