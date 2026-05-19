"""create profesores table

Revision ID: 8046da311f1f
Revises: 2a0f539e0942
Create Date: 2026-05-14 10:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8046da311f1f'
down_revision: Union[str, Sequence[str], None] = '2a0f539e0942'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('profesores',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('grado_id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(100), nullable=False),
    sa.Column('departamento', sa.String(100), nullable=False),
    sa.ForeignKeyConstraint(['grado_id'], ['grados_academicos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_profesores_id'), 'profesores', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_profesores_id'), table_name='profesores')
    op.drop_table('profesores')
