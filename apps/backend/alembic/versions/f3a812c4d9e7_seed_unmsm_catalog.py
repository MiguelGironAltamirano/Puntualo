"""seed unmsm universities and faculties

Revision ID: f3a812c4d9e7
Revises: c1d2e3f4a5b6
Create Date: 2026-05-25 19:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f3a812c4d9e7"
down_revision: Union[str, Sequence[str], None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_UNIVERSITY = {
    "name": "Universidad Nacional Mayor de San Marcos",
    "city": "Lima",
    "country": "Perú",
}

_FACULTIES = [
    "Facultad de Ciencias Administrativas",
    "Facultad de Ciencias Biológicas",
    "Facultad de Ciencias Contables",
    "Facultad de Ciencias Económicas",
    "Facultad de Ciencias Físicas",
    "Facultad de Ciencias Matemáticas",
    "Facultad de Ciencias Sociales",
    "Facultad de Derecho y Ciencia Política",
    "Facultad de Educación",
    "Facultad de Farmacia y Bioquímica",
    "Facultad de Ingeniería de Sistemas e Informática",
    "Facultad de Ingeniería Electrónica y Eléctrica",
    "Facultad de Ingeniería Geológica, Minera, Metalúrgica y Geográfica",
    "Facultad de Ingeniería Industrial",
    "Facultad de Letras y Ciencias Humanas",
    "Facultad de Medicina",
    "Facultad de Medicina Veterinaria",
    "Facultad de Odontología",
    "Facultad de Psicología",
    "Facultad de Química e Ingeniería Química",
]


def upgrade() -> None:
    bind = op.get_bind()

    university_id = bind.execute(
        sa.text(
            "INSERT INTO universities (name, city, country) "
            "VALUES (:name, :city, :country) "
            "ON CONFLICT (name) DO UPDATE SET city = EXCLUDED.city "
            "RETURNING id"
        ),
        _UNIVERSITY,
    ).scalar_one()

    for faculty_name in _FACULTIES:
        bind.execute(
            sa.text(
                "INSERT INTO faculties (university_id, name) "
                "VALUES (:university_id, :name) "
                "ON CONFLICT (name, university_id) DO NOTHING"
            ),
            {"university_id": university_id, "name": faculty_name},
        )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "DELETE FROM faculties "
            "WHERE university_id IN (SELECT id FROM universities WHERE name = :name) "
            "AND name = ANY(:names)"
        ),
        {"name": _UNIVERSITY["name"], "names": _FACULTIES},
    )
    bind.execute(
        sa.text("DELETE FROM universities WHERE name = :name"),
        {"name": _UNIVERSITY["name"]},
    )
