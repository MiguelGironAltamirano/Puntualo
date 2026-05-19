from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Like(Base):

    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint("usuario_id", "resena_id", name="uq_likes_usuario_resena"),
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

    resena_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("resenas.id"),
        nullable=False
    )

    fecha: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
