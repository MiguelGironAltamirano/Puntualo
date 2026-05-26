"""merge

Revision ID: 5120b34ec1e5
Revises: d7e8f9a0b1c2, f3a812c4d9e7
Create Date: 2026-05-26 14:39:52.567260

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5120b34ec1e5'
down_revision: Union[str, Sequence[str], None] = ('d7e8f9a0b1c2', 'f3a812c4d9e7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
