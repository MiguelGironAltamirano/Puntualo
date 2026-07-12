"""Tool: comparación de profesores por NOMBRE, en UNA sola llamada.

El historial del chat solo tiene nombres (no UUIDs), y pedirle al modelo que
re-busque cada nombre y luego compare exige encadenar rondas de tools — el
punto donde falla y termina prometiendo "dame un momento" sin poder cumplir.
Aquí la resolución nombre→id y la comparación se hacen server-side.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.chatbot.tools.compare_professors import compare_professors
from app.services.chatbot.tools.resolve_professor import resolve_professors_by_name


async def compare_professors_by_name(*, db: AsyncSession, names: list[str]) -> dict:
    resolved: dict[str, str] = {}  # full_name -> professor_id
    unresolved: list[str] = []
    for name in names:
        matches = await resolve_professors_by_name(db, name, limit=1)
        if matches:
            resolved[matches[0].full_name] = str(matches[0].id)
        else:
            unresolved.append(name)

    if len(resolved) < 2:
        return {
            "found": False,
            "resolved": resolved,
            "unresolved": unresolved,
            "note": (
                "No se pudieron resolver al menos 2 profesores con esos nombres. "
                "Informa honestamente al usuario; NUNCA inventes datos."
            ),
        }

    result = await compare_professors(db=db, professor_ids=list(resolved.values()))
    result["found"] = True
    result["resolved"] = resolved
    if unresolved:
        result["unresolved"] = unresolved
    return result
