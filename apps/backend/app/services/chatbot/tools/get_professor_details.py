"""Tool: detalle completo de un profesor con su resumen IA."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.professors.service import ProfessorService
from app.services.chatbot.tools.resolve_professor import resolve_professors_by_name


async def get_professor_details(
    *,
    db: AsyncSession,
    professor_id: str | None = None,
    professor_name: str | None = None,
) -> dict:
    """Devuelve el detalle de un profesor por UUID o por nombre.

    Acepta nombre porque el historial del chat solo conserva texto: exigir el
    UUID obligaría al LLM a encadenar una búsqueda previa (donde suele fallar).

    get_detail retorna una tupla:
      (professor, courses, degrees, evidence, summary,
       university_name, faculty_name, ai_summary_row, ai_summary_reason)
    o None si no existe.

    Nunca expone user_id ni datos de identidad del llamador.
    """
    if not professor_id and professor_name:
        matches = await resolve_professors_by_name(db, professor_name, limit=1)
        if not matches:
            return {
                "found": False,
                "professor_name": professor_name,
                "note": "No existe un profesor validado con ese nombre.",
            }
        professor_id = str(matches[0].id)
    if not professor_id:
        return {"found": False, "note": "Falta professor_id o professor_name."}

    service = ProfessorService(db)
    result = await service.get_detail(professor_id)

    if result is None:
        return {"found": False, "professor_id": professor_id}

    (
        professor,
        courses,
        degrees,
        _evidence,
        summary,
        university_name,
        faculty_name,
        ai_summary_row,
        _ai_summary_reason,
    ) = result

    return {
        "found": True,
        "professor_id": str(professor.id),
        "full_name": professor.full_name,
        "faculty_id": professor.faculty_id,
        "faculty_name": faculty_name,
        "university_name": university_name,
        "global_score": (
            float(professor.global_score) if professor.global_score is not None else None
        ),
        "total_evaluations": professor.total_evaluations,
        "courses": [c.name for c in courses],
        "executive_summary": summary,
        "ai_summary": ai_summary_row.summary if ai_summary_row is not None else None,
    }
