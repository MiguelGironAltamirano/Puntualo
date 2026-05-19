"""Calculo del semestre academico actual (funcion pura).

Convencion: dos semestres por anio. Enero-Julio => "YYYY-1"; Agosto-Diciembre
=> "YYYY-2". `settings.SEMESTER_OVERRIDE` permite forzar el valor desde tests
o entornos especiales.
"""
from datetime import datetime, timezone

from app.core.config import settings


def current_semester(now: datetime | None = None) -> str:
    """Retorna el semestre actual con formato "YYYY-1" | "YYYY-2"."""
    if settings.SEMESTER_OVERRIDE:
        return settings.SEMESTER_OVERRIDE
    if now is None:
        now = datetime.now(timezone.utc)
    half = 1 if now.month <= 7 else 2
    return f"{now.year}-{half}"
