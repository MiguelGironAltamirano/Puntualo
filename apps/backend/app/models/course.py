import uuid

from sqlalchemy import ForeignKey, Index, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class Course(Base, TimestampMixin, SoftDeleteMixin):

    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    university_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("universities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    faculty_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("faculties.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index(
            "uq_courses_name_university_active",
            func.lower(text("name")),
            text("university_id"),
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
    )
