"""Celery tasks de NLP — Tarea 4.4 (resumen ejecutivo asíncrono).

Patrón calcado de professor_validation_tasks.py: NullPool+asyncpg, asyncio.run,
ciclo AiJob, idempotencia. `_run_summary` es la corutina testeable.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Callable

import redis.asyncio as aioredis
from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.async_session import _build_async_url
from app.models.ai_job import AiJob
from app.services.nlp.gemini_client import GeminiClient
from app.services.nlp.summary_generator import generate_and_store

logger = logging.getLogger(__name__)


def _make_db_session() -> async_sessionmaker[AsyncSession]:
    url, connect_args = _build_async_url(settings.DATABASE_URL)
    engine = create_async_engine(url, poolclass=NullPool, connect_args=connect_args)
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)


async def _has_running_job(professor_id: str, db: AsyncSession) -> bool:
    row = (
        await db.execute(
            select(AiJob).where(
                AiJob.job_type == "summary_generation",
                AiJob.status == "running",
                AiJob.input_payload["professor_id"].astext == professor_id,
            ).limit(1)
        )
    ).scalar_one_or_none()
    return row is not None


async def _run_summary(
    professor_id: str,
    *,
    session_factory: Callable[[], AsyncSession] | None = None,
    force: bool = False,
) -> None:
    """Corutina pura. En prod abre su propia sesión; en tests recibe la del fixture."""
    if session_factory is None:
        SessionLocal = _make_db_session()
        async with SessionLocal() as db:
            await _do_run(professor_id, db, force=force)
            await db.commit()
        return
    db = session_factory()
    await _do_run(professor_id, db, force=force)
    await db.flush()


async def _do_run(professor_id: str, db: AsyncSession, *, force: bool) -> None:
    if not force and await _has_running_job(professor_id, db):
        logger.info("nlp.task.skip_running | professor_id=%s", professor_id)
        return

    now = datetime.now(timezone.utc)
    job = AiJob(
        job_type="summary_generation",
        status="running",
        started_at=now,
        input_payload={"professor_id": professor_id, "force": force},
    )
    db.add(job)
    await db.flush()

    try:
        payload = await generate_and_store(professor_id, db, force=force)
        job.status = "completed"
        job.finished_at = datetime.now(timezone.utc)
        if payload is None:
            job.result_payload = {"skipped": True, "reason": "guard_not_met"}
        else:
            job.result_payload = {
                "model_version": payload["model_version"],
                "token_usage": payload["token_usage"],
                "reviews_used": payload["reviews_used"],
            }
        await db.flush()
    except Exception as exc:
        job.status = "failed"
        job.finished_at = datetime.now(timezone.utc)
        job.error_message = str(exc)[:500]
        await db.flush()
        raise


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    acks_late=True,
    name="nlp.generate_summary",
)
def generate_professor_summary(self, professor_id: str, force: bool = False) -> None:
    professor_id = str(professor_id)
    import app.utils.cache as _cache
    _cache.redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    logger.info("nlp.task.start | professor_id=%s | force=%s", professor_id, force)
    try:
        asyncio.run(_run_summary(professor_id, force=force))
        logger.info("nlp.task.done | professor_id=%s", professor_id)
    except Exception as exc:
        logger.error("nlp.task.crash | professor_id=%s | error=%s", professor_id, exc)
        raise self.retry(exc=exc)


from sqlalchemy import func as _func  # noqa: E402

from app.models.comment import Comment as _Comment  # noqa: E402
from app.models.evaluation import Evaluation as _Evaluation  # noqa: E402
from app.models.professor import Professor as _Prof  # noqa: E402
from app.models.professor_ai_summary import ProfessorAiSummary as _Summary  # noqa: E402


async def find_stale_professor_ids(db: AsyncSession) -> list[str]:
    """Profesores que ameritan (re)generación de resumen.

    (a) validated, sin summary, con >= NLP_SUMMARY_MIN_REVIEWS comentarios publicados; o
    (b) con summary, pero con >= IA_SUMMARY_THRESHOLD evaluaciones cuyo updated_at
        es posterior a summary.generated_at.
    """
    published_count = (
        select(_func.count())
        .select_from(_Comment.__table__.join(
            _Evaluation.__table__, _Comment.evaluation_id == _Evaluation.id))
        .where((_Comment.professor_id == _Prof.id) & (_Comment.status == "published"))
        .scalar_subquery()
    )

    no_summary = (
        select(_Prof.id)
        .outerjoin(_Summary, _Summary.professor_id == _Prof.id)
        .where(
            _Prof.validation_status == "validated",
            _Summary.id.is_(None),
            published_count >= settings.NLP_SUMMARY_MIN_REVIEWS,
        )
    )

    new_evals_count = (
        select(_func.count())
        .select_from(_Evaluation.__table__)
        .where(
            (_Evaluation.professor_id == _Prof.id)
            & (_Evaluation.updated_at > _Summary.generated_at)
        )
        .scalar_subquery()
    )
    stale_summary = (
        select(_Prof.id)
        .join(_Summary, _Summary.professor_id == _Prof.id)
        .where(
            _Prof.validation_status == "validated",
            new_evals_count >= settings.IA_SUMMARY_THRESHOLD,
        )
    )

    rows_a = (await db.execute(no_summary)).scalars().all()
    rows_b = (await db.execute(stale_summary)).scalars().all()
    return list({str(r) for r in rows_a} | {str(r) for r in rows_b})


async def _run_enqueue(*, session_factory: Callable[[], AsyncSession] | None = None) -> int:
    async def _inner(db: AsyncSession) -> int:
        ids = await find_stale_professor_ids(db)
        for pid in ids:
            generate_professor_summary.delay(pid)
        return len(ids)

    if session_factory is None:
        SessionLocal = _make_db_session()
        async with SessionLocal() as db:
            return await _inner(db)
    return await _inner(session_factory())


@shared_task(name="nlp.enqueue_pending_summaries")
def enqueue_pending_summaries() -> int:
    logger.info("nlp.enqueue.start")
    n = asyncio.run(_run_enqueue())
    logger.info("nlp.enqueue.done | enqueued=%d", n)
    return n
