import uuid

from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class User(Base, TimestampMixin, SoftDeleteMixin):

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    dni: Mapped[str | None] = mapped_column(String, unique=True, nullable=True, default=None)

    career_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("careers.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    role: Mapped[str] = mapped_column(String, nullable=False, default="student")

    provider: Mapped[str] = mapped_column(String, nullable=False, default="local")

    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    strike_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("role IN ('student','admin')", name="ck_users_role"),
    )
