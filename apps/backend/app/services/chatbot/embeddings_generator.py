"""Genera y persiste embeddings de profesores para el retrieval del chatbot."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.professor import Professor
from app.models.professor_ai_summary import ProfessorAiSummary
from app.models.professor_embedding import ProfessorEmbedding
from app.services.chatbot.cohere_client import CohereEmbedder

logger = logging.getLogger(__name__)

_TOP_HASHTAGS = 10


def build_source_text(*, full_name: str, summary: str, pros: list[str],
                      cons: list[str], hashtags: list[str]) -> str:
    """Texto canónico que se embebe por profesor."""
    parts = [f"Profesor: {full_name}", f"Resumen: {summary}"]
    if pros:
        parts.append("Fortalezas: " + "; ".join(pros))
    if cons:
        parts.append("Debilidades: " + "; ".join(cons))
    if hashtags:
        parts.append("Etiquetas: " + ", ".join(hashtags))
    return "\n".join(parts)


async def _top_hashtags(db: AsyncSession, professor_id: uuid.UUID, limit: int = _TOP_HASHTAGS) -> list[str]:
    # Recupera los hashtags más frecuentes asociados a las evaluaciones del profesor
    rows = await db.execute(text("""
        SELECT h.label
        FROM evaluation_hashtags eh
        JOIN hashtags h ON h.id = eh.hashtag_id
        JOIN evaluations e ON e.id = eh.evaluation_id
        WHERE e.professor_id = :pid
        GROUP BY h.label
        ORDER BY COUNT(*) DESC
        LIMIT :lim
    """), {"pid": str(professor_id), "lim": limit})
    return [r[0] for r in rows]


async def generate_and_store(
    professor_id: uuid.UUID | str,
    db: AsyncSession,
    *,
    embedder: CohereEmbedder | None = None,
) -> bool:
    """Genera el embedding del profesor desde su resumen IA y lo upserta.

    Devuelve False si el profesor no tiene resumen (no se puede embeber).
    """
    embedder = embedder or CohereEmbedder()
    prof = (await db.execute(
        select(Professor).where(Professor.id == professor_id)
    )).scalar_one_or_none()
    summary = (await db.execute(
        select(ProfessorAiSummary).where(ProfessorAiSummary.professor_id == professor_id)
    )).scalar_one_or_none()

    if prof is None or summary is None:
        logger.info("chat.embeddings.skip_no_summary | professor_id=%s", professor_id)
        return False

    hashtags = await _top_hashtags(db, prof.id)
    source = build_source_text(
        full_name=prof.full_name,
        summary=summary.summary,
        pros=list(summary.pros),
        cons=list(summary.cons),
        hashtags=hashtags,
    )
    vector = (await embedder.embed_documents([source]))[0]

    now = datetime.now(timezone.utc)
    if db.bind.dialect.name == "sqlite":
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert
        insert_fn = sqlite_insert
    else:
        insert_fn = pg_insert

    stmt = insert_fn(ProfessorEmbedding).values(
        professor_id=prof.id,
        embedding=vector,
        embedding_model=settings.COHERE_EMBED_MODEL,
        source_version=summary.model_version,
        generated_at=now,
        updated_at=now,
    ).on_conflict_do_update(
        index_elements=["professor_id"],
        set_={
            "embedding": vector,
            "embedding_model": settings.COHERE_EMBED_MODEL,
            "source_version": summary.model_version,
            "generated_at": now,
            "updated_at": now,
        },
    )
    await db.execute(stmt)
    logger.info("chat.embeddings.stored | professor_id=%s", professor_id)
    return True
