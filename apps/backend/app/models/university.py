from sqlalchemy import BigInteger, Identity, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class University(Base, TimestampMixin):

    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Perú")

    __table_args__ = (
        UniqueConstraint("name", name="uq_universities_name"),
    )
