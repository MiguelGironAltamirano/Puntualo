from sqlalchemy import BigInteger, ForeignKey, Identity, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class Course(Base, TimestampMixin, SoftDeleteMixin):

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    university_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("universities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    faculty_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("faculties.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)

    __table_args__ = (
        Index(
            "uq_courses_name_university_active",
            func.lower(text("name")),
            text("university_id"),
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
    )
