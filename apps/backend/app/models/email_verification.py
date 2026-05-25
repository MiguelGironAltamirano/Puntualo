import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class EmailVerification(Base, TimestampMixin):

    __tablename__ = "email_verifications"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    dni: Mapped[str | None] = mapped_column(String, nullable=True, unique=True, default=None)

    career_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("careers.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    code_hash: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
