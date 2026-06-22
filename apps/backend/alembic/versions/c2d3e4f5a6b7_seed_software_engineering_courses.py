"""seed Ingeniería de Software career and courses under FISI-UNMSM

Revision ID: c2d3e4f5a6b7
Revises: 20ba82fe5276
Create Date: 2026-06-21 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c2d3e4f5a6b7"
down_revision: Union[str, Sequence[str], None] = "20ba82fe5276"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_UNIVERSITY_NAME = "Universidad Nacional Mayor de San Marcos"
_FACULTY_NAME = "Facultad de Ingeniería de Sistemas e Informática"
_CAREER_NAME = "Ingeniería de Software"

_COURSES = [
    # prerequisito
    "Redaccion y tecnicas de comunicación efectiva",
    # ciclo 1
    "Metodos de estudios universitarios",
    "Desarrollo personal y liderazgo",
    "Calculo I",
    "Biologia para ciencias e ingenieria",
    "Algebra y geometria analitica",
    "Medio ambiente y desarrollo sostenible",
    "Programacion y computacion",
    # ciclo 2
    "Investigacion formativa",
    "Realidad nacional y mundial",
    "Calculo II",
    "Fisica I",
    "Quimica general",
    "Introduccion a las ciencias e ingenieria",
    "Emprendimiento e innovacion",
    # ciclo 3
    "Algoritmica I",
    "Estadistica y probabilidades",
    "Fisica electronica",
    "Ingenieria economica",
    "Introduccion al desarrollo de software",
    "Matematica basica",
    # ciclo 4
    "Algoritmica II",
    "Estructura de datos",
    "Sistemas digitales",
    "Organizacion y administracion",
    "Contabilidad para la gestion",
    "Procesos de software",
    "Matematica discreta",
    # ciclo 5
    "Analisis y diseño de algoritmos",
    "Base de datos I",
    "Lenguajes y compiladores",
    "Computacion visual",
    "Economia para la gestión",
    "Ingenieria de requisitos",
    "Arquitectura de computadoras",
    # ciclo 6
    "Base de datos II",
    "Diseño de software",
    "Calidad de software",
    "Etica profesional y legislacion informatica",
    "Gestión de proyecto de software",
    "Interacción hombre computador",
    "Sistemas operativos",
    # ciclo 7
    "Inteligencia artificial",
    "Gestion de la configuracion y mantenimiento del software",
    "Arquitectura de software",
    "Pruebas de software",
    "Experiencia de usuario y usabilidad",
    "Formacion de empresas de software",
    "Redes y transmisión de datos",
    # ciclo 8
    "Inteligencia de negocios",
    "Aseguramiento de la calidad del software",
    "Metodologia de la investigacion",
    "Taller de construcción de software web",
    "Mineria de datos",
    "Programacion concurrente y paralela",
    "Automatizacion y control de software",
    # ciclo 9
    "Software inteligente",
    "Desarrollo de tesis I",
    "Gerencia de tecnologia de la información",
    "Gestion de riesgo del software",
    "Taller de construccion de software movil",
    "Seguridad del software",
    "Internet de las cosas",
    # ciclo 10
    "Analitica de datos",
    "Desarrollo de tesis II",
    "Taller de aplicaciones sociales",
    "Tendencias en ingenieria de software",
    "Innovacion, tecnologia y emprendimiento",
    "Practica pre profesional",
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

    # Insert career (idempotent)
    bind.execute(
        sa.text(
            "INSERT INTO careers (faculty_id, name) "
            "VALUES (:f, :n) "
            "ON CONFLICT (name, faculty_id) DO NOTHING"
        ),
        {"f": faculty_id, "n": _CAREER_NAME},
    )
    career_id = bind.execute(
        sa.text("SELECT id FROM careers WHERE name = :n AND faculty_id = :f"),
        {"n": _CAREER_NAME, "f": faculty_id},
    ).scalar()

    for name in _COURSES:
        # Insert course (idempotent — unique on lower(name) + university_id)
        bind.execute(
            sa.text(
                "INSERT INTO courses (name, university_id, faculty_id, is_active) "
                "VALUES (:n, :u, :f, TRUE) "
                "ON CONFLICT DO NOTHING"
            ),
            {"n": name, "u": uni_id, "f": faculty_id},
        )
        # Link to career using lower() lookup to handle case variants already in DB
        bind.execute(
            sa.text(
                "INSERT INTO career_courses (career_id, course_id) "
                "SELECT :career_id, id FROM courses "
                "WHERE lower(name) = lower(:n) AND university_id = :u AND is_active = TRUE "
                "ON CONFLICT DO NOTHING"
            ),
            {"career_id": career_id, "n": name, "u": uni_id},
        )


def downgrade() -> None:
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

    career_id = bind.execute(
        sa.text("SELECT id FROM careers WHERE name = :n AND faculty_id = :f"),
        {"n": _CAREER_NAME, "f": faculty_id},
    ).scalar()

    if career_id is not None:
        bind.execute(
            sa.text("DELETE FROM career_courses WHERE career_id = :c"),
            {"c": career_id},
        )
        bind.execute(
            sa.text("DELETE FROM careers WHERE id = :c"),
            {"c": career_id},
        )

    bind.execute(
        sa.text(
            "DELETE FROM courses "
            "WHERE university_id = :u AND faculty_id = :f AND name = ANY(:names)"
        ),
        {"u": uni_id, "f": faculty_id, "names": _COURSES},
    )
