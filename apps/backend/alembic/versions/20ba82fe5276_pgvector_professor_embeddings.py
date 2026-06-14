"""pgvector professor_embeddings

Revision ID: 20ba82fe5276
Revises: b2c3d4e5f6a7
Create Date: 2026-06-13 23:16:48.395397

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '20ba82fe5276'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "professor_embeddings",
        sa.Column("professor_id", PGUUID(as_uuid=True),
                  sa.ForeignKey("professors.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("embedding_model", sa.Text(), nullable=False),
        sa.Column("source_version", sa.Text(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    op.execute(
        "CREATE INDEX professor_embeddings_hnsw_idx "
        "ON professor_embeddings USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.drop_index("professor_embeddings_hnsw_idx", table_name="professor_embeddings")
    op.drop_table("professor_embeddings")
    # No se elimina la extensión vector: puede haber otros objetos que la usen.
