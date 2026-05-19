"""create likes table

Revision ID: e417c40fa6cf
Revises: 75b636c05a3f
Create Date: 2026-05-14 10:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e417c40fa6cf'
down_revision: Union[str, Sequence[str], None] = '75b636c05a3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('likes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.String(), nullable=False),
    sa.Column('resena_id', sa.Integer(), nullable=False),
    sa.Column('fecha', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    sa.ForeignKeyConstraint(['resena_id'], ['resenas.id'], ),
    sa.ForeignKeyConstraint(['usuario_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('usuario_id', 'resena_id')
    )
    op.create_index(op.f('ix_likes_id'), 'likes', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_likes_id'), table_name='likes')
    op.drop_table('likes')
