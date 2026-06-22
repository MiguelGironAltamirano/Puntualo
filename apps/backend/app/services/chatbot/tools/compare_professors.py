"""Tool: comparación de profesores. Reusa ComparisonService."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.professors.service_comparison import ComparisonService


def _serialize(obj: object) -> object:
    """Convierte recursivamente datetime→ISO string para garantizar JSON-serializable."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    return obj


async def compare_professors(
    *,
    db: AsyncSession,
    professor_ids: list[str],
) -> dict:
    """Compara dos o más profesores devolviendo métricas y ranking por categoría.

    get_comparison_data retorna dicts que contienen objetos datetime (created_at,
    generated_at), por eso se aplica _serialize antes de devolver.

    Nunca expone user_id ni datos de identidad del llamador.
    """
    service = ComparisonService(db)
    data = await service.get_comparison_data(professor_ids)
    return {"comparison": _serialize(data)}
