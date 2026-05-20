import uuid

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, String, Text, text
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

    file_path: Mapped[str] = mapped_column(Text, nullable=False)

    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)

    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "document_type IN ('carnet','matricula')",
            name="ck_uploaded_documents_type",
        ),
        CheckConstraint(
            "mime_type IN ('image/jpeg','image/png','application/pdf')",
            name="ck_uploaded_documents_mime",
        ),
    )
