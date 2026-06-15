"""Celery tasks de embeddings del chatbot (Tarea 4.5).

Patrón calcado de nlp_tasks.py: NullPool+asyncpg, asyncio.run, corutina testeable.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Callable

from celery import shared_task
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.async_session import _build_async_url
from app.services.chatbot.embeddings_generator import generate_and_store

logger = logging.getLogger(__name__)


def _make_db_session() -> async_sessionmaker[AsyncSession]:
    url, connect_args = _build_async_url(settings.DATABASE_URL)
    engine = create_async_engine(url, poolclass=NullPool, connect_args=connect_args)
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)


async def _run_refresh(
    professor_id: str,
    *,
    session_factory: Callable[[], AsyncSession] | None = None,
) -> None:
    """Corutina pura. En prod abre su propia sesión; en tests recibe la del fixture."""
    if session_factory is None:
        SessionLocal = _make_db_session()
        async with SessionLocal() as db:
            await generate_and_store(professor_id, db)
            await db.commit()
        return
    db = session_factory()
    await generate_and_store(professor_id, db)
    await db.flush()


@shared_task(name="chat.refresh_professor_embedding")
def refresh_professor_embedding(professor_id: str) -> None:
    asyncio.run(_run_refresh(professor_id))


async def _stale_ids(db: AsyncSession) -> list[str]:
    rows = await db.execute(text("""
        SELECT s.professor_id
        FROM professor_ai_summaries s
        LEFT JOIN professor_embeddings e ON e.professor_id = s.professor_id
        WHERE e.professor_id IS NULL OR s.updated_at > e.generated_at
    """))
    return [str(r[0]) for r in rows]


@shared_task(name="chat.enqueue_stale_embeddings")
def enqueue_stale_embeddings() -> int:
    async def _run() -> list[str]:
        SessionLocal = _make_db_session()
        async with SessionLocal() as db:
            return await _stale_ids(db)

    ids = asyncio.run(_run())
    for pid in ids:
        refresh_professor_embedding.delay(pid)
    logger.info("chat.embeddings.enqueue_stale | count=%d", len(ids))
    return len(ids)
