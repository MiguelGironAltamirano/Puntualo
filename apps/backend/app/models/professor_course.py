import uuid

from sqlalchemy import BigInteger, ForeignKey, PrimaryKeyConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ProfessorCourse(Base, TimestampMixin):

    __tablename__ = "professor_courses"

    professor_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("professors.id", ondelete="CASCADE"),
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
        PrimaryKeyConstraint("professor_id", "course_id", name="pk_professor_courses"),
    )
