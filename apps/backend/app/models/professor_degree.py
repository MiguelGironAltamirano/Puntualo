import uuid

from sqlalchemy import BigInteger, ForeignKey, Integer, PrimaryKeyConstraint, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProfessorDegree(Base):

    __tablename__ = "professor_degrees"

    professor_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("professors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    degree_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("academic_degrees.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    institution: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)

    year_obtained: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)

    __table_args__ = (
        PrimaryKeyConstraint("professor_id", "degree_id", name="pk_professor_degrees"),
    )
