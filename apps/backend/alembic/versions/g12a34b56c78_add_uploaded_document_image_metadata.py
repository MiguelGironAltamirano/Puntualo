"""Add image metadata to uploaded documents

Revision ID: g12a34b56c78
Revises: f1a2b3c4d5e6
Create Date: 2026-05-25 12:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "g12a34b56c78"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("uploaded_documents", sa.Column("side", sa.String(length=10), nullable=True))
    op.add_column("uploaded_documents", sa.Column("width_px", sa.Integer(), nullable=True))
    op.add_column("uploaded_documents", sa.Column("height_px", sa.Integer(), nullable=True))
    op.add_column("uploaded_documents", sa.Column("quality_score", sa.Float(), nullable=True))
    op.create_check_constraint(
        "ck_uploaded_documents_side",
        "uploaded_documents",
        "side IS NULL OR side IN ('front','back')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_uploaded_documents_side", "uploaded_documents", type_="check")
    op.drop_column("uploaded_documents", "quality_score")
    op.drop_column("uploaded_documents", "height_px")
    op.drop_column("uploaded_documents", "width_px")
    op.drop_column("uploaded_documents", "side")
