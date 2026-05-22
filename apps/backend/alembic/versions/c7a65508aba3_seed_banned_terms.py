"""seed banned terms

Revision ID: c7a65508aba3
Revises: d2f4a9c1e8b3
Create Date: 2026-05-22 01:31:06.573604

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c7a65508aba3"
down_revision: Union[str, Sequence[str], None] = "d2f4a9c1e8b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_HIGH = [
    "puta", "puto", "mierda", "concha", "carajo", "imbecil", "idiota",
    "estupido", "estupida", "pendejo", "pendeja", "huevon", "huevona",
    "marica", "maricon", "cabron", "cabrona",
]
_MEDIUM = [
    "tonto", "tonta", "feo", "fea", "asqueroso", "asquerosa",
]
_LOW = [
    "mal", "pesimo", "horrible",
]


def upgrade() -> None:
    rows = (
        [{"term": t, "severity": "high"} for t in _HIGH]
        + [{"term": t, "severity": "medium"} for t in _MEDIUM]
        + [{"term": t, "severity": "low"} for t in _LOW]
    )
    op.execute(
        sa.text(
            "INSERT INTO banned_terms (term, severity) VALUES "
            + ", ".join(f"('{r['term']}', '{r['severity']}')" for r in rows)
            + " ON CONFLICT (term) DO NOTHING"
        )
    )


def downgrade() -> None:
    all_terms = _HIGH + _MEDIUM + _LOW
    in_list = ", ".join(f"'{t}'" for t in all_terms)
    op.execute(sa.text(f"DELETE FROM banned_terms WHERE term IN ({in_list})"))
