from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class University(Base):

    __tablename__ = "universidades"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    ciudad: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    pais: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
