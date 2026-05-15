from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Class(Base):

    __tablename__ = "clases"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    profesor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("profesores.id"),
        nullable=False
    )

    universidad_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("universidades.id"),
        nullable=False
    )

    materia_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("materias.id"),
        nullable=False
    )

    codigo: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    horario: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None
    )

    semestre: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    año: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
