import uuid

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, Integer, Numeric, String, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class Professor(Base, TimestampMixin, SoftDeleteMixin):

    __tablename__ = "professors"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    full_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

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

    validation_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending_validation",
    )

    registered_by_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )

    global_score: Mapped[float | None] = mapped_column(
        Numeric(3, 2),
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
            "validation_status IN ('pending_validation','validated','not_found','rejected')",
            name="ck_professors_validation_status",
        ),
        CheckConstraint(
            "global_score IS NULL OR global_score BETWEEN 1.0 AND 5.0",
            name="ck_professors_global_score_range",
        ),
    )
