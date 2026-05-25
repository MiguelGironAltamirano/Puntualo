"""add email verifications table

Revision ID: f1a2b3c4d5e6
Revises: d2f4a9c1e8b3
Create Date: 2026-05-25 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "d2f4a9c1e8b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "email_verifications",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("dni", sa.String(), nullable=True),
        sa.Column("career_id", sa.BigInteger(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("code_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["career_id"], ["careers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_email_verifications_email"),
        sa.UniqueConstraint("username", name="uq_email_verifications_username"),
        sa.UniqueConstraint("dni", name="uq_email_verifications_dni"),
    )
    op.create_index("ix_email_verifications_career_id", "email_verifications", ["career_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_email_verifications_career_id", table_name="email_verifications")
    op.drop_table("email_verifications")
