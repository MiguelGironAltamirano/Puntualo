import uuid

from sqlalchemy import ForeignKey
from sqlalchemy import Index
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

    university: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    faculty: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
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

    __table_args__ = (
        Index(
            "uq_professors_name_university_active",
            func.lower(text("full_name")),
            text("university"),
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
    )
