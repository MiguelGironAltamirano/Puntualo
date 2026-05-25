"""Merge de verificación de emails y términos prohibidos

Revision ID: bbd8f7119421
Revises: c7a65508aba3, f1a2b3c4d5e6
Create Date: 2026-05-25 15:47:39.100620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bbd8f7119421'
down_revision: Union[str, Sequence[str], None] = ('c7a65508aba3', 'f1a2b3c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
