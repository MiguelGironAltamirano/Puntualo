from __future__ import annotations

import asyncio
import logging

import redis.asyncio as aioredis
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.models.professor import Professor
from app.models.professor_evidence import ProfessorEvidence
from app.services.professor_validation.budget import BudgetTracker
from app.services.professor_validation.pipeline import ProfessorValidationPipeline
from app.services.professor_validation.sources.openalex import OpenAlexSource
from app.services.professor_validation.sources.orcid import OrcidSource
from app.services.professor_validation.sources.tavily import TavilySource
from app.services.professor_validation.sources.unmsm_directory import UnmsmDirectorySource

logger = logging.getLogger(__name__)


def _make_db_session() -> async_sessionmaker[AsyncSession]:
    """Create a fresh async engine + session factory using NullPool.

    NullPool prevents connection reuse across event loops — required in Celery prefork workers
    because asyncio.run() creates and destroys a new loop for each task.
    """
    url = settings.DATABASE_URL
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(url, poolclass=NullPool)
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    acks_late=True,
    name="professor_validation.run",
)
def run_professor_validation(self, professor_id: str, full_name: str) -> None:
    """
    Ejecuta el ProfessorValidationPipeline contra los 4 sources y persiste resultados.
    En caso de crash no marca rejected — deja pending para retry o revalidación manual.
    """
    # Reset the module-level redis_client singleton so it binds to the fresh event loop.
    # Celery prefork: asyncio.run() closes its loop after each task; the singleton would
    # hold connections tied to that dead loop on subsequent tasks in the same worker process.
    import app.utils.cache as _cache
    _cache.redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    logger.info(f"validation start | professor_id={professor_id} | name={full_name}")
    try:
        asyncio.run(_run(professor_id, full_name))
        logger.info(f"validation done  | professor_id={professor_id}")
    except Exception as exc:
        logger.error(f"validation crash | professor_id={professor_id} | error={exc}")
        raise self.retry(exc=exc)


async def _run(professor_id: str, full_name: str) -> None:
    # Fresh Redis client for BudgetTracker (bound to this event loop)
    _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    # Fresh DB session factory with NullPool (no cross-loop connection reuse)
    SessionLocal = _make_db_session()

    try:
        budget = BudgetTracker(_redis, env="prod")
        pipeline = ProfessorValidationPipeline(
            sources=[
                UnmsmDirectorySource(),
                OpenAlexSource(),
                OrcidSource(),
                TavilySource(budget=budget),
            ],
            budget=budget,
        )

        professor = _ProfessorStub(professor_id, full_name)
        new_status, evidence_records = await pipeline.run(professor)

        async with SessionLocal() as db:
            prof = await db.get(Professor, professor_id)
            if prof is None:
                logger.warning(f"professor_id={professor_id} not found in DB, skipping persist")
                return

            prof.validation_status = new_status

            for source_name, payload in evidence_records:
                role = "enrichment" if _is_enrichment_payload(payload) else "validation"
                db.add(ProfessorEvidence(
                    professor_id=professor_id,
                    source=source_name,
                    role=role,
                    raw_payload=_serialize_payload(payload),
                ))

            await db.commit()
            logger.info(
                f"validation persisted | professor_id={professor_id} | status={new_status} "
                f"| evidence_count={len(evidence_records)}"
            )
    finally:
        await _redis.aclose()
        import app.utils.cache as _cache
        await _cache.redis_client.aclose()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _ProfessorStub:
    """Objeto mínimo que el pipeline necesita para acceder a full_name."""
    def __init__(self, professor_id: str, full_name: str) -> None:
        self.id = professor_id
        self.full_name = full_name


def _is_enrichment_payload(payload: dict) -> bool:
    """True si el payload contiene FieldWithProvenance (fase enrichment)."""
    if not payload:
        return False
    return any(hasattr(v, "model_dump") for v in payload.values())


def _serialize_payload(payload: dict) -> dict:
    """Convierte FieldWithProvenance a dict JSON-serializable."""
    if not payload:
        return {}
    result = {}
    for k, v in payload.items():
        if hasattr(v, "model_dump"):
            result[k] = v.model_dump(mode="json")
        else:
            result[k] = v
    return result
