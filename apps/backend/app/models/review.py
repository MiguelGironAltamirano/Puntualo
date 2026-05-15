from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReviewStatus(str, Enum):
    PENDING = "pendiente"
    PUBLISHED = "publicada"
    REJECTED = "rechazada"


class Review(Base):

    __tablename__ = "resenas"
    __table_args__ = (
        UniqueConstraint("usuario_id", "clase_id", name="uq_resenas_usuario_clase"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    usuario_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id"),
        nullable=False
    )

    clase_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("clases.id"),
        nullable=False
    )

    comentario: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None
    )

    estado: Mapped[ReviewStatus] = mapped_column(
        SQLEnum(ReviewStatus),
        nullable=False,
        default=ReviewStatus.PENDING
    )

    es_anonima: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    fecha: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
