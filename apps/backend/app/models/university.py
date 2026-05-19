from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class University(Base, TimestampMixin):
    """
    Universidad como entidad de referencia. PK Integer autoincrement (consistente
    con el resto del catálogo de referencia: faculties, academic_degrees).
    UNIQUE(name) — no debería haber dos universidades con el mismo nombre.
    """

    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("name", name="uq_universities_name"),
    )
