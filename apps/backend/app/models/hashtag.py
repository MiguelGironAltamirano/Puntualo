import uuid

from sqlalchemy import BigInteger, ForeignKey, Identity, Index, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Hashtag(Base, TimestampMixin):

    __tablename__ = "hashtags"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    label: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        index=True,
    )

    usage_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    __table_args__ = (
        Index("ix_hashtags_label_gin", "label", postgresql_using="gin",
              postgresql_ops={"label": "gin_trgm_ops"}),
    )
