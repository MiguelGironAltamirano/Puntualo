"""Merge branch metadata de imagenes con main

Revision ID: 5139c8aa0a58
Revises: c1d2e3f4a5b6, g12a34b56c78
Create Date: 2026-05-25 18:58:28.839480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5139c8aa0a58'
down_revision: Union[str, Sequence[str], None] = ('c1d2e3f4a5b6', 'g12a34b56c78')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
