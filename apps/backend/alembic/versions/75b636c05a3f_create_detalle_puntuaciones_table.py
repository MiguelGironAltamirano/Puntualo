"""create detalle_puntuaciones table

Revision ID: 75b636c05a3f
Revises: ef5a73d642ed
Create Date: 2026-05-14 10:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75b636c05a3f'
down_revision: Union[str, Sequence[str], None] = 'ef5a73d642ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('detalle_puntuaciones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('resena_id', sa.Integer(), nullable=False),
    sa.Column('categoria_id', sa.Integer(), nullable=False),
    sa.Column('valor', sa.SmallInteger(), nullable=False),
    sa.CheckConstraint('valor BETWEEN 1 AND 5'),
    sa.ForeignKeyConstraint(['categoria_id'], ['categorias_puntuacion.id'], ),
    sa.ForeignKeyConstraint(['resena_id'], ['resenas.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('resena_id', 'categoria_id')
    )
    op.create_index(op.f('ix_detalle_puntuaciones_id'), 'detalle_puntuaciones', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_detalle_puntuaciones_id'), table_name='detalle_puntuaciones')
    op.drop_table('detalle_puntuaciones')
