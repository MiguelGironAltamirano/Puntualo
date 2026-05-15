"""create clases table

Revision ID: 4b266d847cf4
Revises: 8046da311f1f
Create Date: 2026-05-14 10:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b266d847cf4'
down_revision: Union[str, Sequence[str], None] = '8046da311f1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('clases',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('profesor_id', sa.Integer(), nullable=False),
    sa.Column('universidad_id', sa.Integer(), nullable=False),
    sa.Column('materia_id', sa.Integer(), nullable=False),
    sa.Column('codigo', sa.String(50), nullable=False),
    sa.Column('horario', sa.String(100), nullable=True),
    sa.Column('semestre', sa.String(10), nullable=False),
    sa.Column('año', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['materia_id'], ['materias.id'], ),
    sa.ForeignKeyConstraint(['profesor_id'], ['profesores.id'], ),
    sa.ForeignKeyConstraint(['universidad_id'], ['universidades.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clases_id'), 'clases', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_clases_id'), table_name='clases')
    op.drop_table('clases')
