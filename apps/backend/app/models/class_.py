from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Class(Base):

    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    teacher_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teachers.id"),
        nullable=False
    )

    university_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("universities.id"),
        nullable=False
    )

    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    schedule: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None
    )

    semester: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
