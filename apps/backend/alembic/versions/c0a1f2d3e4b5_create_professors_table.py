"""Create professors table

Revision ID: c0a1f2d3e4b5
Revises: 744b703e5881
Create Date: 2026-05-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0a1f2d3e4b5'
down_revision: Union[str, Sequence[str], None] = '744b703e5881'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'professors',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=False),
        sa.Column('university', sa.String(length=150), nullable=False),
        sa.Column('faculty', sa.String(length=150), nullable=False),
        sa.Column('validation_status', sa.String(length=30), nullable=False, server_default='pending_validation'),
        sa.Column('registered_by_id', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['registered_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_professors_full_name'), 'professors', ['full_name'], unique=False)
    op.create_index(op.f('ix_professors_is_active'), 'professors', ['is_active'], unique=False)
    op.create_index(
        'uq_professors_name_university_active',
        'professors',
        [sa.text('lower(full_name)'), 'university'],
        unique=True,
        postgresql_where=sa.text('is_active = true'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('uq_professors_name_university_active', table_name='professors', postgresql_where=sa.text('is_active = true'))
    op.drop_index(op.f('ix_professors_is_active'), table_name='professors')
    op.drop_index(op.f('ix_professors_full_name'), table_name='professors')
    op.drop_table('professors')
