"""seed complete FISI curricula: Ingenieria de Sistemas, Ciencias de la
Computacion (nuevas carreras) y electivos faltantes de Ingenieria de Software

Fuente: Reporte de Plan de Estudios 2023 del Sistema Unico de Matricula (SUM)
UNMSM, Facultad de Ingenieria de Sistemas e Informatica, para las 3 escuelas
con malla publicada (Ingenieria de Sistemas, Ingenieria de Software, Ciencias
de la Computacion). Inteligencia Artificial es carrera nueva (admision 2026)
sin malla publicada aun, no se siembra.

Revision ID: h1i2j3k4l5m6
Revises: ac0a1108d910
Create Date: 2026-07-12 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "h1i2j3k4l5m6"
down_revision: Union[str, Sequence[str], None] = "ac0a1108d910"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_UNIVERSITY_NAME = "Universidad Nacional Mayor de San Marcos"
_FACULTY_NAME = "Facultad de Ingeniería de Sistemas e Informática"

# Cursos comunes de Estudios Generales, compartidos por las 3 escuelas
# (mismo codigo INO1xx/INO2xx en el plan oficial 2023).
_ESTUDIOS_GENERALES = [
    "Redacción y Técnicas de Comunicación Efectiva I",
    "Métodos de Estudio Universitario",
    "Desarrollo Personal y Liderazgo",
    "Cálculo I",
    "Biología para Ciencias e Ingeniería",
    "Álgebra y Geometría Analítica",
    "Medio Ambiente y Desarrollo Sostenible",
    "Programación y Computación",
    "Redacción y Técnicas de Comunicación Efectiva II",
    "Investigación Formativa",
    "Realidad Nacional y Mundial",
    "Cálculo II",
    "Física I",
    "Química General",
    "Introducción a las Ciencias e Ingeniería",
    "Emprendimiento e Innovación",
]

_CARRERAS = {
    "Ingeniería de Sistemas": _ESTUDIOS_GENERALES + [
        # Ciclo 3
        "Introducción a la Computación",
        "Series y Ecuaciones Diferenciales",
        "Electromagnetismo y Óptica",
        "Programación de Computadoras I",
        "Fundamentos de Sistemas de Información",
        "Matemáticas Discretas",
        # Ciclo 4
        "Organización Empresarial",
        "Programación de Computadoras II",
        "Métodos Numéricos",
        "Arquitectura de Computadoras",
        "Estadística I",
        "Ingeniería Económica",
        # Ciclo 5
        "Análisis de Sistemas de Información",
        "Diseño de Base de Datos",
        "Estructura de Datos",
        "Estadística II",
        "Sistemas Operativos",
        "Investigación Operativa",
        # Ciclo 6
        "Diseño de Sistemas de Información",
        "Administración de Base de Datos",
        "Redes y Comunicaciones",
        "Diseño de Interfases de Usuario",
        "Modelos y Simulación",
        "Finanzas para la Gestión",
        # Ciclo 7
        "Interacción Humano Computador",
        "Desarrollo de Aplicaciones Web",
        "Inteligencia Artificial",
        "Inteligencia de Negocios",
        "Gestión de Datos Masivos",
        "Internet de las Cosas",
        # Ciclo 8
        "Computación Visual",
        "Desarrollo de Aplicaciones Móviles",
        "Sistemas Distribuidos",
        "Sistemas Inteligentes",
        "Gestión de Proyectos de TI",
        "Metodología de la Investigación",
        # Ciclo 9
        "Arquitectura Empresarial",
        "Gestión de Procesos de Negocio",
        "Minería de Datos",
        "Auditoría de Sistemas",
        "Seguridad de la Información",
        "Proyecto de Tesis I",
        # Ciclo 10
        "Gestión de Tecnologías de Información",
        "Arquitectura de Servicios",
        "Tendencias en Sistemas de Información",
        "Proyecto de Fin de Carrera",
        "Ética Profesional y Emprendimiento",
        "Proyecto de Tesis II",
    ],
    "Ciencias de la Computación": _ESTUDIOS_GENERALES + [
        # Electivos ciclo 1
        "Proceso Cultural Andino",
        "Dibujo Técnico",
        "Inglés para Escritura Académica",
        "Matlab",
        "Cálculos Básicos en Química",
        "Seguridad e Higiene en Laboratorio",
        "Fundamentos de Riesgos de Desastres y Cambio Climático",
        "Geografía Económica del Perú",
        "Ciudadanía y Derechos Fundamentales",
        "Taller de Electricidad y Electrónica",
        "Economía General",
        "Taller de Música",
        "Taller de Danza",
        "Apreciación de Cine",
        "Quechua",
        # Ciclo 3
        "Introducción a la Ciencia de la Computación",
        "Programación de Computadoras I",
        "Desarrollo Basado en Plataformas",
        "Estructuras Discretas",
        "Series y Ecuaciones Diferenciales",
        "Ingeniería Económica",
        "Óptica y Electro-Magnetismo",
        # Ciclo 4
        "Algoritmos y Estructuras de Datos",
        "Teoría de la Computación",
        "Base de Datos I",
        "Arquitectura de Computadores",
        "Estadística y Probabilidades",
        "Análisis Numérico",
        # Ciclo 5
        "Análisis y Diseño de Algoritmos",
        "Base de Datos II",
        "Ingeniería de Software I",
        "Sistemas Operativos",
        "Programación de Computadoras II",
        "Investigación Operativa",
        # Ciclo 6
        "Ingeniería de Software II",
        "Redes y Comunicaciones",
        "Estructura de Datos Avanzado",
        "Tópicos de Sistemas Operativos Avanzados",
        "Lenguajes y Compiladores I",
        "Modelos y Simulación",
        "Procesos Estocásticos",
        # Ciclo 7
        "Interacción Humano Computador",
        "Lenguajes y Compiladores II",
        "Computación Paralela y Distribuida",
        "Computación Gráfica",
        "Heurísticas y Meta Heurísticas",
        "Investigación e Innovación",
        # Ciclo 8
        "Seguridad en Computación",
        "Tópicos en Ciencia de Datos",
        "Inteligencia Artificial",
        "Arte y Tecnología",
        "Proyecto Final de Carrera I",
        "Computación Verde",
        # Ciclo 9
        "Tópicos en Inteligencia Artificial",
        "Práctica Preprofesional I",
        "Tópicos en Computación Gráfica",
        "Proyecto Final de Carrera II",
        # Ciclo 10
        "Práctica Preprofesional II",
        "Tecnología Basada en Internet",
        "Bioinformática y Bioestadística",
        "Proyecto Final de Carrera III",
    ],
}

# Electivos y cursos de Ingeniería de Software presentes en el plan oficial
# 2023 pero ausentes en la migración c2d3e4f5a6b7 (que sembró la malla base).
_INGENIERIA_SOFTWARE_CARRERA = "Ingeniería de Software"
_INGENIERIA_SOFTWARE_FALTANTES = [
    "Fundamentos de Riesgos de Desastres y Cambio Climático",
    "Taller de Música",
    "Taller de Danza",
    "Inglés Básico",
    "Seguridad e Higiene Ocupacional",
]


def _get_uni_and_faculty(bind):
    uni_id = bind.execute(
        sa.text("SELECT id FROM universities WHERE name = :n"),
        {"n": _UNIVERSITY_NAME},
    ).scalar()
    if uni_id is None:
        return None, None
    faculty_id = bind.execute(
        sa.text("SELECT id FROM faculties WHERE name = :n AND university_id = :u"),
        {"n": _FACULTY_NAME, "u": uni_id},
    ).scalar()
    return uni_id, faculty_id


def _upsert_course(bind, name, uni_id, faculty_id):
    bind.execute(
        sa.text(
            "INSERT INTO courses (name, university_id, faculty_id, is_active) "
            "VALUES (:n, :u, :f, TRUE) "
            "ON CONFLICT DO NOTHING"
        ),
        {"n": name, "u": uni_id, "f": faculty_id},
    )


def _link_career_course(bind, career_id, name, uni_id):
    bind.execute(
        sa.text(
            "INSERT INTO career_courses (career_id, course_id) "
            "SELECT :career_id, id FROM courses "
            "WHERE lower(name) = lower(:n) AND university_id = :u AND is_active = TRUE "
            "ON CONFLICT DO NOTHING"
        ),
        {"career_id": career_id, "n": name, "u": uni_id},
    )


def upgrade() -> None:
    bind = op.get_bind()
    uni_id, faculty_id = _get_uni_and_faculty(bind)
    if uni_id is None or faculty_id is None:
        return

    for career_name, courses in _CARRERAS.items():
        bind.execute(
            sa.text(
                "INSERT INTO careers (faculty_id, name) "
                "VALUES (:f, :n) "
                "ON CONFLICT (name, faculty_id) DO NOTHING"
            ),
            {"f": faculty_id, "n": career_name},
        )
        career_id = bind.execute(
            sa.text("SELECT id FROM careers WHERE name = :n AND faculty_id = :f"),
            {"n": career_name, "f": faculty_id},
        ).scalar()

        for course_name in courses:
            _upsert_course(bind, course_name, uni_id, faculty_id)
            _link_career_course(bind, career_id, course_name, uni_id)

    # Electivos faltantes de Ingenieria de Software (carrera ya sembrada por
    # c2d3e4f5a6b7)
    software_career_id = bind.execute(
        sa.text("SELECT id FROM careers WHERE name = :n AND faculty_id = :f"),
        {"n": _INGENIERIA_SOFTWARE_CARRERA, "f": faculty_id},
    ).scalar()
    if software_career_id is not None:
        for course_name in _INGENIERIA_SOFTWARE_FALTANTES:
            _upsert_course(bind, course_name, uni_id, faculty_id)
            _link_career_course(bind, software_career_id, course_name, uni_id)


def downgrade() -> None:
    bind = op.get_bind()
    uni_id, faculty_id = _get_uni_and_faculty(bind)
    if uni_id is None or faculty_id is None:
        return

    for career_name, courses in _CARRERAS.items():
        career_id = bind.execute(
            sa.text("SELECT id FROM careers WHERE name = :n AND faculty_id = :f"),
            {"n": career_name, "f": faculty_id},
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

    software_career_id = bind.execute(
        sa.text("SELECT id FROM careers WHERE name = :n AND faculty_id = :f"),
        {"n": _INGENIERIA_SOFTWARE_CARRERA, "f": faculty_id},
    ).scalar()
    if software_career_id is not None:
        bind.execute(
            sa.text(
                "DELETE FROM career_courses WHERE career_id = :c AND course_id IN ("
                "SELECT id FROM courses WHERE lower(name) = ANY(:names) AND university_id = :u"
                ")"
            ),
            {
                "c": software_career_id,
                "names": [n.lower() for n in _INGENIERIA_SOFTWARE_FALTANTES],
                "u": uni_id,
            },
        )
