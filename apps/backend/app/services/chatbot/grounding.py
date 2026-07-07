"""Validación de grounding profesor-curso antes de entregar la respuesta final.

El retrieval semántico (retriever.py) y el LLM pueden citar un profesor que no
dicta el curso que el usuario está pidiendo (el embedding del profesor no
codifica sus cursos). Este módulo hace un chequeo server-side, independiente
de si el LLM usó las tools de curso/profesor: detecta qué cursos activos se
mencionan en la conversación y verifica en `professor_courses` que cualquier
profesor citado en la respuesta final efectivamente dicte alguno de ellos.
"""
from __future__ import annotations

import re

from sqlalchemy import select, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.professor_course import ProfessorCourse

_MENTIONED_COURSES_SQL = sa_text(
    """
    SELECT id, name FROM courses
    WHERE is_active = true AND :convo ILIKE '%' || name || '%'
    """
)

_WARNING_TEMPLATE = (
    "\n\n⚠️ No pude confirmar en el sistema que **{name}** dicte el curso del "
    "que estamos hablando; verifica su ficha antes de tomarlo como recomendación."
)


async def courses_mentioned_in(db: AsyncSession, convo_text: str) -> list[tuple[int, str]]:
    """Cursos activos cuyo nombre aparece como substring del texto de la conversación."""
    if not convo_text.strip():
        return []
    rows = await db.execute(_MENTIONED_COURSES_SQL, {"convo": convo_text})
    return [(r[0], r[1]) for r in rows]


def professors_mentioned_in(
    text: str, known_professors: dict[str, str]
) -> list[tuple[str, str]]:
    """[(full_name, professor_id)] de `known_professors` citados textualmente en `text`."""
    return [
        (name, pid)
        for name, pid in known_professors.items()
        if name and re.search(re.escape(name), text, re.IGNORECASE)
    ]


async def _teaching_pairs(
    db: AsyncSession, professor_ids: list[str], course_ids: list[int]
) -> set[tuple[str, int]]:
    if not professor_ids or not course_ids:
        return set()
    rows = await db.execute(
        select(ProfessorCourse.professor_id, ProfessorCourse.course_id).where(
            ProfessorCourse.professor_id.in_(professor_ids),
            ProfessorCourse.course_id.in_(course_ids),
        )
    )
    return {(str(pid), cid) for pid, cid in rows}


async def append_grounding_warnings(
    *,
    db: AsyncSession,
    text: str,
    convo_text: str,
    known_professors: dict[str, str],
) -> str:
    """Agrega una advertencia visible si un profesor citado no dicta ningún curso
    mencionado en la conversación, en vez de dejar pasar la alucinación en silencio.

    No bloquea ni reescribe la respuesta del LLM: solo añade una nota al final
    para los casos que no se pudieron confirmar contra `professor_courses`.
    """
    if not text or not known_professors:
        return text

    courses = await courses_mentioned_in(db, convo_text)
    if not courses:
        return text

    mentioned = professors_mentioned_in(text, known_professors)
    if not mentioned:
        return text

    course_ids = [cid for cid, _name in courses]
    teaching = await _teaching_pairs(db, [pid for _name, pid in mentioned], course_ids)

    warnings: list[str] = []
    for name, pid in mentioned:
        if not any((pid, cid) in teaching for cid in course_ids):
            warnings.append(_WARNING_TEMPLATE.format(name=name))

    if not warnings:
        return text
    return text + "".join(dict.fromkeys(warnings))
