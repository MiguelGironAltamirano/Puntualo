"""Resolución server-side de nombre de profesor → registro validado.

El historial del chat solo conserva texto (nombres, no UUIDs), así que las
tools que reciben nombres deben re-resolverlos aquí en vez de exigirle al LLM
que encadene una búsqueda previa (encadenar rondas de tools es justamente
donde el modelo falla).
"""
from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.professor import Professor


def _base_stmt():
    return select(Professor).where(
        Professor.is_active.is_(True),
        Professor.validation_status == "validated",
    )


async def resolve_professors_by_name(
    db: AsyncSession, name: str, *, limit: int = 3
) -> list[Professor]:
    """Profesores validados que coinciden con `name`.

    Primero intenta el nombre como substring exacto; si no hay match (el LLM
    puede omitir el título o algún nombre intermedio), cae a exigir cada
    palabra significativa por separado.
    """
    name = name.strip()
    if not name:
        return []

    rows = (await db.execute(
        _base_stmt().where(Professor.full_name.ilike(f"%{name}%")).limit(limit)
    )).scalars().all()
    if rows:
        return list(rows)

    words = [w for w in name.replace(".", " ").split() if len(w) > 2]
    if not words:
        return []
    rows = (await db.execute(
        _base_stmt().where(and_(*[Professor.full_name.ilike(f"%{w}%") for w in words])).limit(limit)
    )).scalars().all()
    return list(rows)
