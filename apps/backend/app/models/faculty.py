from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Faculty(Base, TimestampMixin):
    """
    Facultad de una universidad. PK Integer autoincrement (consistente con
    universities). UNIQUE(name, university_id) — no debería haber dos facultades
    con el mismo nombre dentro de la misma universidad.
    """

    __tablename__ = "faculties"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    university_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("universities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "name",
            "university_id",
            name="uq_faculties_name_university",
        ),
    )
