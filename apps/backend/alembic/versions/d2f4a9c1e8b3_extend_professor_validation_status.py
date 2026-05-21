"""extend professor validation_status with not_found

Revision ID: d2f4a9c1e8b3
Revises: 2b5e3b12a3dd
Create Date: 2026-05-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd2f4a9c1e8b3'
down_revision: Union[str, Sequence[str], None] = '2b5e3b12a3dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_professors_validation_status", "professors", type_="check")
    op.create_check_constraint(
        "ck_professors_validation_status",
        "professors",
        "validation_status IN ('pending_validation','validated','not_found','rejected')",
    )


def downgrade() -> None:
    op.execute(
        "UPDATE professors SET validation_status = 'pending_validation' "
        "WHERE validation_status = 'not_found'"
    )
    op.drop_constraint("ck_professors_validation_status", "professors", type_="check")
    op.create_check_constraint(
        "ck_professors_validation_status",
        "professors",
        "validation_status IN ('pending_validation','validated','rejected')",
    )
