from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import redis.asyncio as aioredis
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.models.ai_job import AiJob
from app.models.professor import Professor
from app.models.professor_evidence import ProfessorEvidence
from app.services.professor_validation.budget import BudgetTracker
from app.services.professor_validation.degrees_extractor import extract_and_persist_degrees
from app.services.professor_validation.pipeline import ProfessorValidationPipeline
from app.services.professor_validation.sources.openalex import OpenAlexSource
from app.services.professor_validation.sources.orcid import OrcidSource
from app.services.professor_validation.sources.tavily import TavilySource
from app.services.professor_validation.sources.unmsm_directory import UnmsmDirectorySource

logger = logging.getLogger(__name__)


def _make_db_session() -> async_sessionmaker[AsyncSession]:
    """Engine + session factory con NullPool.

    NullPool evita reutilización de conexiones entre event loops —
    requerido en workers Celery prefork donde asyncio.run() crea y destruye
    un loop por tarea.
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
    # Resetear el singleton de redis_client para que apunte al loop fresco de este task.
    # Celery prefork: asyncio.run() cierra su loop al terminar; el singleton quedaría
    # con conexiones ligadas a ese loop muerto en tasks subsiguientes del mismo proceso.
    import app.utils.cache as _cache
    _cache.redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    logger.info("validation start | professor_id=%s | name=%s", professor_id, full_name)
    try:
        asyncio.run(_run(professor_id, full_name))
        logger.info("validation done  | professor_id=%s", professor_id)
    except Exception as exc:
        logger.error("validation crash | professor_id=%s | error=%s", professor_id, exc)
        raise self.retry(exc=exc)


async def _run(professor_id: str, full_name: str) -> None:
    _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    SessionLocal = _make_db_session()
    now = datetime.now(timezone.utc)

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

        async with SessionLocal() as db:
            # ------------------------------------------------------------------
            # Idempotencia: no reprocesar si ya fue validado (o rechazado).
            # El endpoint /revalidate siempre resetea a pending_validation antes
            # de encolar, así que encontrar otro estado aquí indica procesamiento
            # duplicado o concurrente.
            # ------------------------------------------------------------------
            prof = await db.get(Professor, professor_id)
            if prof is None:
                logger.warning("professor_id=%s not found in DB, skipping", professor_id)
                return

            if prof.validation_status != "pending_validation":
                logger.info(
                    "skipping validation | professor_id=%s | status=%s (already processed)",
                    professor_id, prof.validation_status,
                )
                return

            # ------------------------------------------------------------------
            # Registrar el job de IA como 'running'
            # ------------------------------------------------------------------
            job = AiJob(
                job_type="professor_validation",
                status="running",
                started_at=now,
                input_payload={"professor_id": professor_id, "full_name": full_name},
            )
            db.add(job)
            await db.flush()  # obtener job.id antes de continuar

            # ------------------------------------------------------------------
            # Ejecutar pipeline
            # ------------------------------------------------------------------
            stub = _ProfessorStub(professor_id, full_name)
            new_status, evidence_records = await pipeline.run(stub)

            # ------------------------------------------------------------------
            # Persistir evidencia
            # ------------------------------------------------------------------
            for rec in evidence_records:
                source_name = rec["source"]
                role = rec["role"]
                payload = rec["payload"]

                db.add(ProfessorEvidence(
                    professor_id=professor_id,
                    source=source_name,
                    role=role,
                    found=rec["found"],
                    affiliation_confirmed=rec["affiliation_confirmed"],
                    confidence=rec["confidence"],
                    raw_payload=_serialize_payload(payload),
                ))

            # ------------------------------------------------------------------
            # Derivar grados académicos desde ORCID (solo si validado)
            # ------------------------------------------------------------------
            degrees_inserted = 0
            if new_status == "validated":
                for rec in evidence_records:
                    if rec["source"] == "orcid" and rec["role"] == "enrichment":
                        edu_field = rec["payload"].get("educations")
                        if edu_field is not None:
                            educations = (
                                edu_field.value
                                if hasattr(edu_field, "value")
                                else []
                            )
                            degrees_inserted = await extract_and_persist_degrees(
                                professor_id, educations, db
                            )
                        break

            # ------------------------------------------------------------------
            # Actualizar profesor y job
            # ------------------------------------------------------------------
            prof.validation_status = new_status

            finished = datetime.now(timezone.utc)
            job.status = "completed"
            job.finished_at = finished
            job.result_payload = {
                "new_status": new_status,
                "evidence_count": len(evidence_records),
                "degrees_inserted": degrees_inserted,
            }

            await db.commit()
            logger.info(
                "validation persisted | professor_id=%s | status=%s | "
                "evidence=%d | degrees=%d",
                professor_id, new_status, len(evidence_records), degrees_inserted,
            )

    except Exception as exc:
        # Intentar marcar el job como fallido antes de propagar
        try:
            async with SessionLocal() as db_err:
                from sqlalchemy import update
                await db_err.execute(
                    update(AiJob)
                    .where(
                        AiJob.job_type == "professor_validation",
                        AiJob.status == "running",
                    )
                    .values(
                        status="failed",
                        finished_at=datetime.now(timezone.utc),
                        error_message=str(exc)[:500],
                    )
                )
                await db_err.commit()
        except Exception as inner:
            logger.warning("could not mark job as failed | error=%s", inner)
        raise

    finally:
        await _redis.aclose()
        import app.utils.cache as _cache
        await _cache.redis_client.aclose()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _ProfessorStub:
    def __init__(self, professor_id: str, full_name: str) -> None:
        self.id = professor_id
        self.full_name = full_name


def _serialize_payload(payload: dict) -> dict:
    """Convierte FieldWithProvenance a dict JSON-serializable para almacenar en JSONB."""
    if not payload:
        return {}
    result = {}
    for k, v in payload.items():
        if hasattr(v, "model_dump"):
            result[k] = v.model_dump(mode="json")
        else:
            result[k] = v
    return result
