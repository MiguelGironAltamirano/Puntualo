"""create catalog tables

Revision ID: 2a0f539e0942
Revises: 744b703e5881
Create Date: 2026-05-14 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a0f539e0942'
down_revision: Union[str, Sequence[str], None] = '744b703e5881'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create grados_academicos table
    op.create_table('grados_academicos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(100), nullable=False),
    sa.Column('nivel', sa.String(50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nombre')
    )
    op.create_index(op.f('ix_grados_academicos_id'), 'grados_academicos', ['id'], unique=False)

    # Create universidades table
    op.create_table('universidades',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(150), nullable=False),
    sa.Column('ciudad', sa.String(100), nullable=False),
    sa.Column('pais', sa.String(100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_universidades_id'), 'universidades', ['id'], unique=False)

    # Create materias table
    op.create_table('materias',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(150), nullable=False),
    sa.Column('area', sa.String(100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_materias_id'), 'materias', ['id'], unique=False)

    # Create categorias_puntuacion table
    op.create_table('categorias_puntuacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(100), nullable=False),
    sa.Column('descripcion', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nombre')
    )
    op.create_index(op.f('ix_categorias_puntuacion_id'), 'categorias_puntuacion', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_categorias_puntuacion_id'), table_name='categorias_puntuacion')
    op.drop_table('categorias_puntuacion')
    op.drop_index(op.f('ix_materias_id'), table_name='materias')
    op.drop_table('materias')
    op.drop_index(op.f('ix_universidades_id'), table_name='universidades')
    op.drop_table('universidades')
    op.drop_index(op.f('ix_grados_academicos_id'), table_name='grados_academicos')
    op.drop_table('grados_academicos')
