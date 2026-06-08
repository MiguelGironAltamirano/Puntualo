"""seed 5 test users for integration/testing

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-07 18:00:00.000000

Inserta 5 usuarios institucionales UNMSM (verificados) para que el equipo
pueda comentar/probar al levantar una BD limpia. La contrasena en texto plano
de los 5 es "111111"; se almacena hasheada con bcrypt (misma funcion que el
backend en app.core.security.hash_password), generada en tiempo de ejecucion.

Idempotente: ON CONFLICT DO NOTHING sobre email/username unicos.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.core.security import hash_password


# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Password en texto plano compartida por los 5 usuarios de prueba.
TEST_PASSWORD = "111111"

TEST_USERS = [
    {"email": "mathias.torres@unmsm.edu.pe", "full_name": "Mathias Torres", "username": "mathias.torres"},
    {"email": "valentina.rojas@unmsm.edu.pe", "full_name": "Valentina Rojas", "username": "valentina.rojas"},
    {"email": "diego.huaman@unmsm.edu.pe", "full_name": "Diego Huaman", "username": "diego.huaman"},
    {"email": "camila.flores@unmsm.edu.pe", "full_name": "Camila Flores", "username": "camila.flores"},
    {"email": "sebastian.quispe@unmsm.edu.pe", "full_name": "Sebastian Quispe", "username": "sebastian.quispe"},
]


def upgrade() -> None:
    """Insert 5 verified test users (idempotente)."""
    bind = op.get_bind()

    insert_sql = sa.text(
        "INSERT INTO users "
        "(id, email, full_name, username, hashed_password, role, provider, "
        " is_verified, strike_count, is_active, created_at, updated_at) "
        "VALUES (gen_random_uuid(), :email, :full_name, :username, :hashed_password, "
        " 'student', 'local', true, 0, true, now(), now()) "
        "ON CONFLICT DO NOTHING"
    )

    for user in TEST_USERS:
        bind.execute(
            insert_sql,
            {
                "email": user["email"].lower(),
                "full_name": user["full_name"],
                "username": user["username"],
                # bcrypt: un hash por usuario; todos verifican contra "111111".
                "hashed_password": hash_password(TEST_PASSWORD),
            },
        )


def downgrade() -> None:
    """Remove the 5 test users by email."""
    emails = [u["email"].lower() for u in TEST_USERS]
    op.get_bind().execute(
        sa.text("DELETE FROM users WHERE email IN :emails").bindparams(
            sa.bindparam("emails", expanding=True)
        ),
        {"emails": emails},
    )
