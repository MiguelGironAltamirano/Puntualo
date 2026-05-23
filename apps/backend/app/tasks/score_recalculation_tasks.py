"""app/tasks/score_recalculation_tasks.py

Recalculo asincrono de professors.global_score + total_evaluations tras
crear/eliminar una evaluacion. Diseñada para invocacion via Celery, pero
expone una corutina interna (`_recalculate_async`) testeable con una session
de tests.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Callable

from celery import shared_task
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.models.evaluation import Evaluation
from app.models.professor import Professor
from app.modules.evaluations.scoring import compute_global_score

logger = logging.getLogger(__name__)


def _make_db_session() -> async_sessionmaker[AsyncSession]:
    """Engine + session factory con NullPool.

    NullPool evita reutilizacion de conexiones entre event loops —
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


async def _recalculate_async(
    professor_id: str,
    *,
    session_factory: Callable[[], AsyncSession] | None = None,
) -> None:
    """Corutina pura. En produccion session_factory=None y se abre una session propia.
    En tests se pasa una lambda que devuelve la session del fixture (con rollback automatico).
    """
    if session_factory is None:
        SessionLocal = _make_db_session()
        async with SessionLocal() as session:
            await _do_recalc(professor_id, session)
            await session.commit()
        return

    session = session_factory()
    # En tests NO commiteamos: el fixture de rollback se encarga de limpiar.
    await _do_recalc(professor_id, session)
    await session.flush()


async def _do_recalc(professor_id: str, session: AsyncSession) -> None:
    """Ejecuta el UPDATE de global_score y total_evaluations sobre la BD."""
    stmt = select(
        func.avg(Evaluation.clarity),
        func.avg(Evaluation.easiness),
        func.avg(Evaluation.helpfulness),
        func.avg(Evaluation.punctuality),
        func.count(Evaluation.id),
    ).where(Evaluation.professor_id == professor_id)
    avg_c, avg_e, avg_h, avg_p, count = (await session.execute(stmt)).one()

    if not count:
        await session.execute(
            update(Professor)
            .where(Professor.id == professor_id)
            .values(global_score=None, total_evaluations=0)
        )
        return

    score = compute_global_score(
        float(avg_c), float(avg_e), float(avg_h), float(avg_p)
    )
    await session.execute(
        update(Professor)
        .where(Professor.id == professor_id)
        .values(global_score=score, total_evaluations=int(count))
    )


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
    name="evaluations.recalculate_professor_score",
)
def recalculate_professor_score(self, professor_id: str) -> None:
    professor_id = str(professor_id)
    logger.info("score_recalc start | professor_id=%s", professor_id)
    try:
        asyncio.run(_recalculate_async(professor_id))
        logger.info("score_recalc done | professor_id=%s", professor_id)
    except Exception as exc:
        logger.error("score_recalc crash | professor_id=%s | error=%s", professor_id, exc)
        raise self.retry(exc=exc)
