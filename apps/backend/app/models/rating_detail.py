from sqlalchemy import CheckConstraint, ForeignKey, Integer, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RatingDetail(Base):

    __tablename__ = "rating_details"
    __table_args__ = (
        UniqueConstraint("review_id", "category_id", name="uq_rating_detail_review_category"),
        CheckConstraint("score BETWEEN 1 AND 5"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    review_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reviews.id"),
        nullable=False
    )

    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rating_categories.id"),
        nullable=False
    )

    score: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )
