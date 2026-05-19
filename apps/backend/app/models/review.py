from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReviewStatus(str, Enum):
    PENDING = "pending"
    PUBLISHED = "published"
    REJECTED = "rejected"


class Review(Base):

    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("user_id", "class_id", name="uq_reviews_user_class"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id"),
        nullable=False
    )

    class_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("classes.id"),
        nullable=False
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None
    )

    status: Mapped[ReviewStatus] = mapped_column(
        SQLEnum(ReviewStatus),
        nullable=False,
        default=ReviewStatus.PENDING
    )

    is_anonymous: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    fecha: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
