"""Retrieval semántico de profesores para el chatbot (Tarea 4.5).

Usa pgvector (cosine) sobre professor_embeddings; si no hay embeddings, cae a
una búsqueda textual ILIKE sobre el resumen IA.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.professor import Professor
from app.models.professor_ai_summary import ProfessorAiSummary
from app.models.professor_embedding import ProfessorEmbedding
from app.services.chatbot.cohere_client import CohereEmbedder

logger = logging.getLogger(__name__)


@dataclass
class RetrievedProfessor:
    professor_id: str
    full_name: str
    faculty_name: str | None
    global_score: float | None
    summary: str
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)


def format_context(profs: list[RetrievedProfessor]) -> str:
    if not profs:
        return "No se recuperaron profesores relevantes."
    blocks = []
    for p in profs:
        score = f"{p.global_score:.1f}" if p.global_score is not None else "sin puntaje"
        tags = ", ".join(p.hashtags) if p.hashtags else "—"
        blocks.append(
            f"- {p.full_name} (id={p.professor_id}, facultad={p.faculty_name or '—'}, "
            f"puntaje={score})\n  Resumen: {p.summary}\n  Etiquetas: {tags}"
        )
    return "\n".join(blocks)


class Retriever:
    def __init__(self, db: AsyncSession, *, embedder: CohereEmbedder | None = None) -> None:
        self.db = db
        self.embedder = embedder or CohereEmbedder()

    async def _has_embeddings(self) -> bool:
        row = await self.db.execute(select(ProfessorEmbedding.professor_id).limit(1))
        return row.first() is not None

    async def retrieve(self, query: str, *, top_k: int | None = None) -> list[RetrievedProfessor]:
        top_k = top_k or settings.CHATBOT_TOP_K
        if await self._has_embeddings():
            try:
                qvec = await self.embedder.embed_query(query)
                return await self._semantic(qvec, top_k)
            except Exception:  # Cohere caído → degradar a textual
                logger.warning("chat.retriever.embed_failed_fallback_ilike", exc_info=True)
        return await self._textual(query, top_k)

    async def _semantic(self, qvec: list[float], top_k: int) -> list[RetrievedProfessor]:
        # validation_status es String(30); el valor canónico es "validated" (ver models/professor.py)
        stmt = (
            select(Professor, ProfessorAiSummary)
            .join(ProfessorEmbedding, ProfessorEmbedding.professor_id == Professor.id)
            .join(ProfessorAiSummary, ProfessorAiSummary.professor_id == Professor.id)
            .where(
                Professor.is_active.is_(True),
                Professor.validation_status == "validated",
            )
            .order_by(ProfessorEmbedding.embedding.cosine_distance(qvec))
            .limit(top_k)
        )
        rows = (await self.db.execute(stmt)).all()
        return [await self._to_dto(prof, summ) for prof, summ in rows]

    async def _textual(self, query: str, top_k: int) -> list[RetrievedProfessor]:
        like = f"%{query}%"
        stmt = (
            select(Professor, ProfessorAiSummary)
            .join(ProfessorAiSummary, ProfessorAiSummary.professor_id == Professor.id)
            .where(
                Professor.is_active.is_(True),
                Professor.validation_status == "validated",
                ProfessorAiSummary.summary.ilike(like),
            )
            .order_by(Professor.global_score.desc().nullslast())
            .limit(top_k)
        )
        rows = (await self.db.execute(stmt)).all()
        return [await self._to_dto(prof, summ) for prof, summ in rows]

    async def _to_dto(self, prof: Professor, summ: ProfessorAiSummary) -> RetrievedProfessor:
        tags = await self.db.execute(text("""
            SELECT h.label FROM evaluation_hashtags eh
            JOIN hashtags h ON h.id = eh.hashtag_id
            JOIN evaluations e ON e.id = eh.evaluation_id
            WHERE e.professor_id = :pid GROUP BY h.label ORDER BY COUNT(*) DESC LIMIT 5
        """), {"pid": str(prof.id)})
        # faculty_name no se resuelve aquí; el resumen IA ya basta para el contexto del chatbot
        faculty_name = None
        return RetrievedProfessor(
            professor_id=str(prof.id),
            full_name=prof.full_name,
            faculty_name=faculty_name,
            global_score=prof.global_score,
            summary=summ.summary,
            pros=list(summ.pros),
            cons=list(summ.cons),
            hashtags=[r[0] for r in tags],
        )
