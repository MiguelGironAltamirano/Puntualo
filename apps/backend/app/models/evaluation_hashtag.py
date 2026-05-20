import uuid

from sqlalchemy import BigInteger, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class EvaluationHashtag(Base, TimestampMixin):

    __tablename__ = "evaluation_hashtags"

    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("evaluations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    hashtag_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("hashtags.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        PrimaryKeyConstraint("evaluation_id", "hashtag_id", name="pk_evaluation_hashtags"),
    )
