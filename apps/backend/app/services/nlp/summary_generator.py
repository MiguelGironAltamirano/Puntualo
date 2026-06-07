"""Generación del resumen ejecutivo NLP (Tarea 4.4).

`select_reviews` arma el input (comentarios publicados + criterios numéricos)
con sampling cuando hay demasiadas reseñas. `generate_and_store` orquesta:
guards → input → Gemini → parse → upsert en professor_ai_summaries.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.config import settings
from app.models.comment import Comment
from app.models.evaluation import Evaluation
from app.models.professor import Professor as _Professor
from app.models.professor_ai_summary import ProfessorAiSummary
from app.services.nlp.gemini_client import GeminiClient
from app.services.nlp.prompts import CURRENT_PROMPT_VERSION, SYSTEM_PROMPT, build_user_content

logger = logging.getLogger(__name__)


def _row_to_review(row) -> dict:
    return {
        "comment": row.text,
        "clarity": row.clarity,
        "easiness": row.easiness,
        "helpfulness": row.helpfulness,
        "punctuality": row.punctuality,
    }


async def select_reviews(professor_id: str, db) -> list[dict]:
    """Comentarios publicados + criterios numéricos. Aplica sampling y truncado.

    Si el total supera NLP_SUMMARY_MAX_REVIEWS: toma SAMPLE_RECENT más recientes
    + SAMPLE_RANDOM aleatorios del resto (diversidad temporal). Luego trunca por
    presupuesto de caracteres (~NLP_SUMMARY_MAX_INPUT_TOKENS * 4).
    """
    # SQLite type processors require uuid.UUID objects (not raw strings).
    prof_uuid = uuid.UUID(professor_id) if isinstance(professor_id, str) else professor_id

    base_cols = (
        Comment.id,
        Comment.text,
        Comment.created_at,
        Evaluation.clarity,
        Evaluation.easiness,
        Evaluation.helpfulness,
        Evaluation.punctuality,
    )
    join = Comment.__table__.join(
        Evaluation.__table__, Comment.evaluation_id == Evaluation.id
    )
    where = (Comment.professor_id == prof_uuid) & (Comment.status == "published")

    total = (
        await db.execute(
            select(func.count()).select_from(join).where(where)
        )
    ).scalar_one()

    max_reviews = settings.NLP_SUMMARY_MAX_REVIEWS
    if total <= max_reviews:
        rows = (
            await db.execute(
                select(*base_cols).select_from(join).where(where)
                .order_by(Comment.created_at.desc())
            )
        ).all()
    else:
        n_recent = settings.NLP_SUMMARY_SAMPLE_RECENT
        n_random = settings.NLP_SUMMARY_SAMPLE_RANDOM
        recent = (
            await db.execute(
                select(*base_cols).select_from(join).where(where)
                .order_by(Comment.created_at.desc()).limit(n_recent)
            )
        ).all()
        recent_ids = {r.id for r in recent}
        rest = (
            await db.execute(
                select(*base_cols).select_from(join)
                .where(where & Comment.id.notin_(recent_ids))
                .order_by(func.random()).limit(n_random)
            )
        ).all()
        rows = list(recent) + list(rest)

    # Truncado por presupuesto de caracteres (no recorta comentarios individuales).
    char_budget = settings.NLP_SUMMARY_MAX_INPUT_TOKENS * 4
    reviews: list[dict] = []
    used = 0
    for row in rows:
        review = _row_to_review(row)
        cost = len((review["comment"] or "")) + 40  # +40 por los criterios numéricos
        if used + cost > char_budget and reviews:
            break
        reviews.append(review)
        used += cost
    return reviews


# ---------------------------------------------------------------------------
# generate_and_store — Tarea 4.4
# ---------------------------------------------------------------------------

def model_version() -> str:
    return f"{CURRENT_PROMPT_VERSION}+{settings.GEMINI_MODEL}"


async def published_comment_count(professor_id: uuid.UUID, db) -> int:
    return (
        await db.execute(
            select(func.count()).select_from(Comment.__table__.join(
                Evaluation.__table__, Comment.evaluation_id == Evaluation.id
            )).where(
                (Comment.professor_id == professor_id) & (Comment.status == "published")
            )
        )
    ).scalar_one()


async def generate_and_store(
    professor_id: str,
    db,
    *,
    client: GeminiClient | None = None,
    force: bool = False,
) -> dict | None:
    """Orquesta la generación. Devuelve el payload o None si un guard la bloquea.

    Guards: profesor 'validated' y >= NLP_SUMMARY_MIN_REVIEWS comentarios publicados.
    NO commitea: el caller (task / endpoint) controla la transacción.
    """
    prof_uuid = uuid.UUID(professor_id) if isinstance(professor_id, str) else professor_id

    professor = await db.get(_Professor, prof_uuid)
    if professor is None:
        logger.warning("nlp.generate.no_professor | id=%s", professor_id)
        return None
    if professor.validation_status != "validated":
        logger.info(
            "nlp.generate.skip_not_validated | id=%s | status=%s",
            professor_id, professor.validation_status,
        )
        return None

    count = await published_comment_count(prof_uuid, db)
    if count < settings.NLP_SUMMARY_MIN_REVIEWS:
        logger.info("nlp.generate.skip_insufficient | id=%s | count=%d", professor_id, count)
        return None

    reviews = await select_reviews(professor_id, db)
    client = client or GeminiClient()
    result = await client.generate(
        system_instruction=SYSTEM_PROMPT,
        user_content=build_user_content(professor.full_name, reviews),
    )

    version = model_version()
    now = datetime.now(timezone.utc)
    stmt = (
        pg_insert(ProfessorAiSummary)
        .values(
            professor_id=prof_uuid,
            summary=result.summary,
            pros=result.pros,
            cons=result.cons,
            model_version=version,
            generated_at=now,
        )
        .on_conflict_do_update(
            constraint="uq_professor_ai_summaries_professor",
            set_=dict(
                summary=result.summary,
                pros=result.pros,
                cons=result.cons,
                model_version=version,
                generated_at=now,
            ),
        )
    )
    await db.execute(stmt)
    await db.flush()

    return {
        "summary": result.summary,
        "pros": result.pros,
        "cons": result.cons,
        "model_version": version,
        "token_usage": result.token_usage,
        "reviews_used": len(reviews),
    }
