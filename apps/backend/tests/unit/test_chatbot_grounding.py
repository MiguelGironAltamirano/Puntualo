"""Tests de la validación de grounding profesor-curso (no commitear).

Cubre el fix del bug: el chatbot recomendaba profesores que no dictan el
curso discutido, porque el retrieval semántico no filtra por curso. Este
módulo agrega una advertencia cuando un profesor citado en la respuesta no
está en `professor_courses` para ningún curso mencionado en la conversación.
"""
from sqlalchemy.sql import Select

from app.services.chatbot.grounding import (
    append_grounding_warnings,
    professors_mentioned_in,
)


class FakeDB:
    """Diferencia la query de cursos (sa_text) de la de professor_courses (Select)."""

    def __init__(self, course_rows, teaching_rows):
        self.course_rows = course_rows
        self.teaching_rows = teaching_rows

    async def execute(self, stmt, params=None):
        return self.teaching_rows if isinstance(stmt, Select) else self.course_rows


def test_professors_mentioned_in_encuentra_nombre_exacto():
    known = {"Mtro. Winston Ignacio Ugaz Cachay": "p1", "Otro Profesor": "p2"}
    text = "Te recomiendo al Mtro. Winston Ignacio Ugaz Cachay para ese curso."
    found = professors_mentioned_in(text, known)
    assert found == [("Mtro. Winston Ignacio Ugaz Cachay", "p1")]


async def test_sin_known_professors_no_toca_la_db():
    # known_professors vacío: debe devolver el texto tal cual sin llamar a db.execute.
    class BoomDB:
        async def execute(self, *a, **kw):
            raise AssertionError("no debería consultarse la BD")

    text = "cualquier respuesta"
    out = await append_grounding_warnings(
        db=BoomDB(), text=text, convo_text="Análisis y Diseño de Sistemas", known_professors={},
    )
    assert out == text


async def test_agrega_advertencia_si_profesor_no_dicta_el_curso_mencionado():
    db = FakeDB(
        course_rows=[(10, "Análisis y Diseño de Sistemas")],
        teaching_rows=[],  # Winston no dicta el curso 10
    )
    text = "Te recomiendo al Mtro. Winston Ignacio Ugaz Cachay, es menos exigente."
    out = await append_grounding_warnings(
        db=db,
        text=text,
        convo_text="... Análisis y Diseño de Sistemas ...",
        known_professors={"Mtro. Winston Ignacio Ugaz Cachay": "p-winston"},
    )
    assert text in out
    assert "No pude confirmar" in out
    assert "Mtro. Winston Ignacio Ugaz Cachay" in out


async def test_no_agrega_advertencia_si_el_profesor_si_dicta_el_curso():
    db = FakeDB(
        course_rows=[(10, "Análisis y Diseño de Sistemas")],
        teaching_rows=[("p-gustavo", 10)],
    )
    text = "Te recomiendo al Mtro. Gustavo Arredondo Castillo."
    out = await append_grounding_warnings(
        db=db,
        text=text,
        convo_text="... Análisis y Diseño de Sistemas ...",
        known_professors={"Mtro. Gustavo Arredondo Castillo": "p-gustavo"},
    )
    assert out == text


async def test_sin_curso_mencionado_no_agrega_advertencia():
    db = FakeDB(course_rows=[], teaching_rows=[])
    text = "Te recomiendo al Mtro. Winston Ignacio Ugaz Cachay."
    out = await append_grounding_warnings(
        db=db,
        text=text,
        convo_text="conversación sin ningún curso reconocible",
        known_professors={"Mtro. Winston Ignacio Ugaz Cachay": "p-winston"},
    )
    assert out == text
