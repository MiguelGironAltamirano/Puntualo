"""Tests de la validación de grounding profesor-curso (no commitear).

Cubre el fix del bug: el chatbot recomendaba profesores que no dictan el
curso discutido, porque el retrieval semántico no filtra por curso. Este
módulo agrega una advertencia cuando un profesor citado en la respuesta no
está en `professor_courses` para ningún curso mencionado en la conversación.
"""
from sqlalchemy.sql import Select

from app.services.chatbot.grounding import (
    append_grounding_warnings,
    check_grounding,
    correction_instruction,
    professors_mentioned_in,
)


class FakeDB:
    """Enruta las tres queries: cursos y nombres (sa_text) y professor_courses (Select)."""

    def __init__(self, course_rows, teaching_rows, named_rows=()):
        self.course_rows = course_rows
        self.teaching_rows = teaching_rows
        self.named_rows = list(named_rows)  # [(id, full_name)] de professors

    async def execute(self, stmt, params=None):
        if isinstance(stmt, Select):
            return self.teaching_rows
        return self.named_rows if "FROM professors" in str(stmt) else self.course_rows


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


async def test_check_grounding_detecta_profesor_inventado():
    """CP-RB-03 · Unitario · Basado en riesgo · R5 prompt injection · Respuesta del chatbot con profesor inventado · 1. Invocar check_grounding · ok = False, invented contiene el profesor inventado"""
    # Nombre con título académico que no vino de tools ni existe en `professors`.
    db = FakeDB(course_rows=[(3, "Cálculo I")], teaching_rows=[], named_rows=[])
    check = await check_grounding(
        db=db,
        text="Te recomiendo al Ing. Rafael Adolfo Quiñones Romaní para Cálculo I.",
        convo_text="profe para Cálculo I",
        known_professors={},
    )
    assert not check.ok
    assert check.invented == ["Ing. Rafael Adolfo Quiñones Romaní"]


async def test_check_grounding_profesor_real_citado_de_memoria_se_valida_por_curso():
    # No vino de tools este turno, pero existe en la BD: se valida contra professor_courses.
    db = FakeDB(
        course_rows=[(10, "Cálculo I")],
        teaching_rows=[("p-real", 10)],
        named_rows=[("p-real", "Dr. Juan Pérez Rojas")],
    )
    check = await check_grounding(
        db=db,
        text="Como te dije, el Dr. Juan Pérez Rojas es buena opción para Cálculo I.",
        convo_text="profe para Cálculo I",
        known_professors={},
    )
    assert check.ok


async def test_check_grounding_reporta_ungrounded_y_cursos():
    db = FakeDB(
        course_rows=[(10, "Análisis y Diseño de Sistemas")],
        teaching_rows=[],
    )
    check = await check_grounding(
        db=db,
        text="Te recomiendo al Mtro. Winston Ignacio Ugaz Cachay.",
        convo_text="... Análisis y Diseño de Sistemas ...",
        known_professors={"Mtro. Winston Ignacio Ugaz Cachay": "p-winston"},
    )
    assert not check.ok
    assert check.ungrounded == [("Mtro. Winston Ignacio Ugaz Cachay", "p-winston")]
    assert check.courses == [(10, "Análisis y Diseño de Sistemas")]


async def test_correction_instruction_nombra_profesor_y_curso():
    db = FakeDB(course_rows=[(10, "Cálculo I")], teaching_rows=[])
    check = await check_grounding(
        db=db,
        text="Te recomiendo a Prof X.",
        convo_text="profe para Cálculo I",
        known_professors={"Prof X": "p1"},
    )
    msg = correction_instruction(check)
    assert "Prof X" in msg
    assert "Cálculo I" in msg
    assert "Reescribe" in msg


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
