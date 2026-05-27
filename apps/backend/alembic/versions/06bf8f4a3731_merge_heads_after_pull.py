"""merge heads after pull

Revision ID: 06bf8f4a3731
Revises: 5120b34ec1e5, 5139c8aa0a58
Create Date: 2026-05-26 19:16:41.869037

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06bf8f4a3731'
down_revision: Union[str, Sequence[str], None] = ('5120b34ec1e5', '5139c8aa0a58')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
