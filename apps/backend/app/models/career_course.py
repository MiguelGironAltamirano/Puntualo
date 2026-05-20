from sqlalchemy import BigInteger, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CareerCourse(Base):

    __tablename__ = "career_courses"

    career_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("careers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    course_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("courses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        PrimaryKeyConstraint("career_id", "course_id", name="pk_career_courses"),
    )
