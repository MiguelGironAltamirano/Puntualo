import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Evaluation(Base, TimestampMixin):
    """
    Una evaluación por (user, professor, course, semester). No es borrable
    (preserva la historia del puntaje del profesor). 5 métricas en escala 1..5;
    las primeras 4 entran al global_score del profesor, course_difficulty se
    captura como metadato pero NO entra al puntaje.
    """

    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    professor_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("professors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    course_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("courses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    semester: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
    )

    clarity: Mapped[int] = mapped_column(Integer, nullable=False)
    easiness: Mapped[int] = mapped_column(Integer, nullable=False)
    helpfulness: Mapped[int] = mapped_column(Integer, nullable=False)
    punctuality: Mapped[int] = mapped_column(Integer, nullable=False)
    course_difficulty: Mapped[int] = mapped_column(Integer, nullable=False)

    modality: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "professor_id",
            "course_id",
            "semester",
            name="uq_evaluations_user_professor_course_semester",
        ),
        CheckConstraint("clarity BETWEEN 1 AND 5", name="ck_evaluations_clarity"),
        CheckConstraint("easiness BETWEEN 1 AND 5", name="ck_evaluations_easiness"),
        CheckConstraint("helpfulness BETWEEN 1 AND 5", name="ck_evaluations_helpfulness"),
        CheckConstraint("punctuality BETWEEN 1 AND 5", name="ck_evaluations_punctuality"),
        CheckConstraint("course_difficulty BETWEEN 1 AND 5", name="ck_evaluations_difficulty"),
        CheckConstraint(
            "modality IN ('virtual','presencial','ambas')",
            name="ck_evaluations_modality",
        ),
    )
