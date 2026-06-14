"""Add report escalated column and new report reasons

Revision ID: c9d8e7f6a5b4
Revises: 06bf8f4a3731
Create Date: 2026-06-10 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9d8e7f6a5b4'
down_revision: Union[str, Sequence[str], None] = '06bf8f4a3731'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add escalated column to comment_reports
    op.add_column('comment_reports', sa.Column('escalated', sa.Boolean(), nullable=False, server_default='false'))

    # Drop the old CHECK constraint on reason
    op.drop_constraint('ck_reports_reason', 'comment_reports', type_='check')

    # Create new CHECK constraint with expanded reason values
    op.create_check_constraint(
        'ck_reports_reason',
        'comment_reports',
        "reason IN ('spam','hate_speech','harassment','off_topic','false_information','impersonation','privacy_violation','other')"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the new CHECK constraint
    op.drop_constraint('ck_reports_reason', 'comment_reports', type_='check')

    # Restore the old CHECK constraint with original reason values
    op.create_check_constraint(
        'ck_reports_reason',
        'comment_reports',
        "reason IN ('spam','hate_speech','harassment','off_topic','other')"
    )

    # Remove escalated column
    op.drop_column('comment_reports', 'escalated')
