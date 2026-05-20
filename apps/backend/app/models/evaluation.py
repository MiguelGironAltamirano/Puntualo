import uuid

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Evaluation(Base, TimestampMixin):
    """
    Una evaluación por (user, professor, course, semester). No es borrable
    (preserva la historia del puntaje del profesor). 4 métricas en escala 1..5
    alimentan el global_score del docente.
    """

    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

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

    semester: Mapped[str] = mapped_column(String(7), nullable=False)

    clarity: Mapped[int] = mapped_column(Integer, nullable=False)
    easiness: Mapped[int] = mapped_column(Integer, nullable=False)
    helpfulness: Mapped[int] = mapped_column(Integer, nullable=False)
    punctuality: Mapped[int] = mapped_column(Integer, nullable=False)

    modality: Mapped[str] = mapped_column(String(15), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "user_id", "professor_id", "course_id", "semester",
            name="uq_evaluations_user_professor_course_semester",
        ),
        CheckConstraint("clarity BETWEEN 1 AND 5", name="ck_evaluations_clarity"),
        CheckConstraint("easiness BETWEEN 1 AND 5", name="ck_evaluations_easiness"),
        CheckConstraint("helpfulness BETWEEN 1 AND 5", name="ck_evaluations_helpfulness"),
        CheckConstraint("punctuality BETWEEN 1 AND 5", name="ck_evaluations_punctuality"),
        CheckConstraint(
            "modality IN ('virtual','presencial','ambas')",
            name="ck_evaluations_modality",
        ),
    )
