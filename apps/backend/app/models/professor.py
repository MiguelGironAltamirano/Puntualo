import uuid

from sqlalchemy import CheckConstraint
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base
from app.models.mixins import SoftDeleteMixin
from app.models.mixins import TimestampMixin


class Professor(Base, TimestampMixin, SoftDeleteMixin):

    __tablename__ = "professors"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
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

    validation_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending_validation",
    )

    registered_by_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )

    global_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        default=None,
    )

    total_evaluations: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    __table_args__ = (
        Index(
            "uq_professors_name_university_active",
            func.lower(text("full_name")),
            text("university_id"),
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
        CheckConstraint(
            "global_score IS NULL OR global_score BETWEEN 1.0 AND 5.0",
            name="ck_professors_global_score_range",
        ),
    )
