"""Merge multiple heads

Revision ID: ac0a1108d910
Revises: c2d3e4f5a6b7, c9d8e7f6a5b4
Create Date: 2026-06-26 22:08:55.278720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac0a1108d910'
down_revision: Union[str, Sequence[str], None] = ('c2d3e4f5a6b7', 'c9d8e7f6a5b4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
