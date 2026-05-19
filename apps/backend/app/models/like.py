from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Like(Base):

    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint("user_id", "review_id", name="uq_likes_user_review"),
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

    review_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reviews.id"),
        nullable=False
    )

    fecha: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
