from sqlalchemy import CheckConstraint, ForeignKey, Integer, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RatingDetail(Base):

    __tablename__ = "detalle_puntuaciones"
    __table_args__ = (
        UniqueConstraint("resena_id", "categoria_id", name="uq_detalle_resena_categoria"),
        CheckConstraint("valor BETWEEN 1 AND 5"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    resena_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("resenas.id"),
        nullable=False
    )

    categoria_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("categorias_puntuacion.id"),
        nullable=False
    )

    valor: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )
