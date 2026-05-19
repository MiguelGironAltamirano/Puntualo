from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Teacher(Base):
    """
    Teacher model from review platform schema.
    This maps to the 'teachers' table in the database schema specification.
    Note: There is also a 'Professor' model that maps to 'professors' table
    for professor validation purposes.
    """

    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    degree_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("academic_degrees.id"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    department: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
