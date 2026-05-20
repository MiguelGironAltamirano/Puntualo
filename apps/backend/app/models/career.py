from sqlalchemy import BigInteger, ForeignKey, Identity, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Career(Base, TimestampMixin):

    __tablename__ = "careers"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    faculty_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("faculties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "faculty_id", name="uq_careers_name_faculty"),
    )
