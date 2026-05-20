from sqlalchemy import BigInteger, CheckConstraint, Identity, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class BannedTerm(Base, TimestampMixin):

    __tablename__ = "banned_terms"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    term: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    severity: Mapped[str] = mapped_column(String(10), nullable=False, default="high")

    __table_args__ = (
        CheckConstraint(
            "severity IN ('low','medium','high')",
            name="ck_banned_terms_severity",
        ),
    )
