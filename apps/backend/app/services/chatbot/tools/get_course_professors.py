"""Tool: profesores de un curso mencionado por nombre, en UNA sola llamada.

Combina search_courses + search_professors server-side. Existe porque el
modelo de chat falla con frecuencia en encadenar las dos llamadas en rondas
sucesivas (se queda con el curso resuelto y alucina los profesores); con la
composición hecha aquí, resolver la consulta más común del chatbot deja de
depender de que el LLM encadene tools.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.chatbot.tools.search_courses import search_courses
from app.services.chatbot.tools.search_professors import search_professors


async def get_course_professors(*, db: AsyncSession, course_name: str) -> dict:
    courses = await search_courses(db=db, query=course_name)
    if not courses:
        return {
            "found": False,
            "note": (
                "No existe un curso activo con ese nombre. Informa honestamente "
                "al usuario; NUNCA inventes cursos ni profesores."
            ),
        }
    course = courses[0]
    professors = await search_professors(db=db, course_id=course["course_id"])
    result: dict = {
        "found": True,
        "course": course,
        "professors": professors,
    }
    if len(courses) > 1:
        result["other_matching_courses"] = courses[1:]
    if not professors:
        result["note"] = (
            "El curso existe pero no tiene profesores registrados. Informa "
            "honestamente al usuario; NUNCA inventes nombres de profesores."
        )
    return result
