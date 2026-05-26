import uuid

from sqlalchemy import BigInteger, CheckConstraint, Float, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class UploadedDocument(Base, TimestampMixin):

    __tablename__ = "uploaded_documents"

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

    document_type: Mapped[str] = mapped_column(String(20), nullable=False)

    side: Mapped[str | None] = mapped_column(String(10), nullable=True, default=None)

    file_path: Mapped[str] = mapped_column(Text, nullable=False)

    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)

    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)

    width_px: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    height_px: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)

    __table_args__ = (
        CheckConstraint(
            "document_type IN ('carnet','matricula')",
            name="ck_uploaded_documents_type",
        ),
        CheckConstraint(
            "side IS NULL OR side IN ('front','back')",
            name="ck_uploaded_documents_side",
        ),
        CheckConstraint(
            "mime_type IN ('image/jpeg','image/png','application/pdf')",
            name="ck_uploaded_documents_mime",
        ),
    )
