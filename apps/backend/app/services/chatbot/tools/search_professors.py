"""Tool: búsqueda de profesores. Llama a ProfessorService (capa service)."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.professors.service import ProfessorService


async def search_professors(
    *,
    db: AsyncSession,
    query: str = "",
    course_id: int | None = None,
    faculty_id: int | None = None,
) -> list[dict]:
    """Devuelve hasta CHATBOT_TOP_K profesores que coincidan con `query`.

    `query` es opcional: con solo course_id/faculty_id lista todos los
    profesores validados de ese curso/facultad (el modelo suele llamarla así).

    - Sólo incluye profesores con validation_status='validated'.
    - Ordena por global_score descendente.
    - Nunca expone user_id ni datos de identidad del llamador.
    """
    service = ProfessorService(db)
    stmt = service.list_query(
        search=query or None,
        course_id=course_id,
        faculty_id=faculty_id,
        validation_status="validated",
        hide_rejected=True,
        sort_by="global_score",
        sort_order="desc",
    )
    rows = (await db.execute(stmt.limit(settings.CHATBOT_TOP_K))).scalars().all()
    return [
        {
            "professor_id": str(p.id),
            "full_name": p.full_name,
            "faculty_id": p.faculty_id,
            "global_score": float(p.global_score) if p.global_score is not None else None,
            "total_evaluations": p.total_evaluations,
        }
        for p in rows
    ]
