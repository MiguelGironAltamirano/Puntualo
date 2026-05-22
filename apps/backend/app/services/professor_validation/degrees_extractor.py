from __future__ import annotations

import logging
import unicodedata

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academic_degree import AcademicDegree
from app.models.professor_degree import ProfessorDegree

logger = logging.getLogger(__name__)

# Orden importa: doctorate antes de master para evitar que "doctor" matchee "master"
_LEVEL_KEYWORDS: dict[str, list[str]] = {
    "doctorate": ["doctor", "doctorado", "phd", "ph.d"],
    "master": ["maestria", "maestría", "master", "magister", "magíster", "mg."],
    "specialization": ["especializacion", "especialización", "specialization", "diplomado"],
    "bachelor": ["licenciatura", "ingenieria", "ingeniería", "pregrado", "bachelor", "undergraduate", "bachiller"],
}


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return text.lower().strip()


def _map_level(role_title: str) -> str | None:
    normalized = _normalize(role_title)
    for level, keywords in _LEVEL_KEYWORDS.items():
        if any(kw in normalized for kw in keywords):
            return level
    return None


async def extract_and_persist_degrees(
    professor_id: str,
    educations: list[dict],
    db: AsyncSession,
) -> int:
    """
    Procesa la lista de educations de ORCID y persiste en academic_degrees + professor_degrees.
    Cada dict debe tener: role (título), organization (institución), year_obtained (int|None).
    Retorna el número de filas insertadas en professor_degrees.
    """
    inserted = 0

    for edu in educations:
        role_title = (edu.get("role") or "").strip()
        institution = (edu.get("organization") or "").strip() or None
        year_obtained = edu.get("year_obtained")

        if not role_title:
            continue

        # Truncar títulos muy largos (academic_degrees.name VARCHAR(100))
        role_title = role_title[:100]

        level = _map_level(role_title)
        if level is None:
            logger.debug("degrees_extractor: no level mapping for '%s', skipping", role_title)
            continue

        # Buscar o crear el grado académico
        stmt = select(AcademicDegree).where(AcademicDegree.name == role_title)
        degree = (await db.execute(stmt)).scalar_one_or_none()

        if degree is None:
            degree = AcademicDegree(name=role_title, level=level)
            db.add(degree)
            await db.flush()  # obtener degree.id antes del INSERT de professor_degree

        # Verificar si la asociación ya existe (idempotente)
        pd_stmt = select(ProfessorDegree).where(
            ProfessorDegree.professor_id == professor_id,
            ProfessorDegree.degree_id == degree.id,
        )
        if (await db.execute(pd_stmt)).scalar_one_or_none() is not None:
            continue

        db.add(ProfessorDegree(
            professor_id=professor_id,
            degree_id=degree.id,
            institution=institution,
            year_obtained=int(year_obtained) if year_obtained is not None else None,
        ))
        inserted += 1

    return inserted
