"""Tool: búsqueda de cursos por nombre. Resuelve nombre → course_id.

Permite al LLM encontrar el course_id de un curso mencionado por el usuario
(ej. "Análisis y Diseño de Sistemas") antes de filtrar profesores con
search_professors(course_id=...), en lugar de depender solo del retrieval
semántico (que no filtra por curso).
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.evaluations.service.course_service import CourseService


async def search_courses(
    *,
    db: AsyncSession,
    query: str,
    university_id: int | None = None,
) -> list[dict]:
    """Devuelve hasta CHATBOT_TOP_K cursos activos que coincidan con `query`."""
    service = CourseService(db)
    stmt = service.list_query(q=query, university_id=university_id)
    rows = (await db.execute(stmt.limit(settings.CHATBOT_TOP_K))).scalars().all()
    return [
        {
            "course_id": c.id,
            "name": c.name,
            "faculty_id": c.faculty_id,
            "university_id": c.university_id,
        }
        for c in rows
    ]
