import uuid

from sqlalchemy import ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class UserStrike(Base, TimestampMixin):
    """
    Bitácora de strikes recibidos por un usuario. Cada fila referencia el
    comentario removido y la decisión de IA que originó el strike. Al
    acumularse 3 strikes, el servicio desactiva la cuenta
    (users.is_active = false, users.strike_count = 3).
    """

    __tablename__ = "user_strikes"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    comment_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    moderation_action_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("moderation_actions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
