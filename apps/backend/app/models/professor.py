from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Professor(Base):

    __tablename__ = "profesores"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    grado_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("grados_academicos.id"),
        nullable=False
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    departamento: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
