"""seed additional FISI courses for testing

Revision ID: a1b2c3d4e5f6
Revises: 06bf8f4a3731
Create Date: 2026-05-31 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "06bf8f4a3731"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_UNIVERSITY_NAME = "Universidad Nacional Mayor de San Marcos"
_FACULTY_NAME = "Facultad de Ingeniería de Sistemas e Informática"

_COURSES = [
    "Programación I",
    "Programación II",
    "Cálculo I",
    "Cálculo II",
    "Matemática Discreta",
    "Sistemas Operativos",
    "Redes de Computadoras",
    "Inteligencia Artificial",
    "Arquitectura de Computadoras",
    "Análisis y Diseño de Sistemas",
    "Programación Web",
    "Seguridad Informática",
    "Estadística y Probabilidades",
    "Compiladores",
    "Gestión de Proyectos de Software",
]


def upgrade() -> None:
    bind = op.get_bind()

    uni_id = bind.execute(
        sa.text("SELECT id FROM universities WHERE name = :n"),
        {"n": _UNIVERSITY_NAME},
    ).scalar()
    if uni_id is None:
        return

    faculty_id = bind.execute(
        sa.text("SELECT id FROM faculties WHERE name = :n AND university_id = :u"),
        {"n": _FACULTY_NAME, "u": uni_id},
    ).scalar()
    if faculty_id is None:
        return

    for name in _COURSES:
        bind.execute(
            sa.text(
                "INSERT INTO courses (name, university_id, faculty_id, is_active) "
                "VALUES (:n, :u, :f, TRUE) "
                "ON CONFLICT DO NOTHING"
            ),
            {"n": name, "u": uni_id, "f": faculty_id},
        )


def downgrade() -> None:
    bind = op.get_bind()
    uni_id = bind.execute(
        sa.text("SELECT id FROM universities WHERE name = :n"),
        {"n": _UNIVERSITY_NAME},
    ).scalar()
    if uni_id is None:
        return

    bind.execute(
        sa.text("DELETE FROM courses WHERE university_id = :u AND name = ANY(:names)"),
        {"u": uni_id, "names": _COURSES},
    )
