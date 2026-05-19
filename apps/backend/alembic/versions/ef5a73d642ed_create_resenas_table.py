"""create resenas table

Revision ID: ef5a73d642ed
Revises: 4b266d847cf4
Create Date: 2026-05-14 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef5a73d642ed'
down_revision: Union[str, Sequence[str], None] = '4b266d847cf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop preventivo del tipo por si quedó huérfano de un upgrade previo fallido.
    # SQLAlchemy auto-crea el ENUM cuando `op.create_table` ve la columna `estado`,
    # así que NO debe llamarse `.create()` explícito antes (causa DuplicateObject).
    op.execute("DROP TYPE IF EXISTS resena_estado")

    op.create_table('resenas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.String(), nullable=False),
    sa.Column('clase_id', sa.Integer(), nullable=False),
    sa.Column('comentario', sa.Text(), nullable=True),
    sa.Column(
        'estado',
        sa.Enum('pendiente', 'publicada', 'rechazada', name='resena_estado'),
        nullable=False,
        server_default='pendiente',
    ),
    sa.Column('es_anonima', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('fecha', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    sa.ForeignKeyConstraint(['clase_id'], ['clases.id'], ),
    sa.ForeignKeyConstraint(['usuario_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('usuario_id', 'clase_id')
    )
    op.create_index(op.f('ix_resenas_id'), 'resenas', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_resenas_id'), table_name='resenas')
    op.drop_table('resenas')
    # Drop ENUM type
    sa.Enum('pendiente', 'publicada', 'rechazada', name='resena_estado').drop(op.get_bind())
