"""app/modules/evaluations/service/hashtag_service.py

normalize_upsert_many: pipeline para procesar la lista de hashtags enviada
con una evaluacion. Garantiza:
  - max 5 etiquetas (post-dedup),
  - cada label normalizada + formato valido,
  - hashtags NUEVOS pasan banned_terms_filter (severity threshold 'low'),
  - hashtags ya existentes solo incrementan usage_count.

autocomplete: prefijo case-insensitive, ordenado por usage_count DESC.
"""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.db import escape_like

from app.models.hashtag import Hashtag
from app.modules.evaluations.errors import (
    HashtagBannedTermsError,
    HashtagLimitExceededError,
)
from app.modules.evaluations.schemas import HashtagSuggestion
from app.utils.hashtag_normalizer import normalize, validate_format
from app.utils.moderation import banned_terms_filter

MAX_HASHTAGS_PER_EVAL = 5


class HashtagService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def normalize_upsert_many(
        self,
        *,
        raw_labels: list[str],
        created_by_id: uuid.UUID,
    ) -> list[Hashtag]:
        if not raw_labels:
            return []

        # 1) Normalizar y deduplicar manteniendo orden de primera aparicion.
        normalized: list[str] = []
        seen: set[str] = set()
        for raw in raw_labels:
            label = normalize(raw)
            if not label:
                continue
            if label in seen:
                continue
            validate_format(label)
            seen.add(label)
            normalized.append(label)

        if not normalized:
            return []

        # 2) Limite de 5 (post-dedup, antes de tocar BD).
        if len(normalized) > MAX_HASHTAGS_PER_EVAL:
            raise HashtagLimitExceededError()

        # 3) Buscar cuales ya existen.
        existing_stmt = select(Hashtag).where(Hashtag.label.in_(normalized))
        existing_rows = (await self.db.execute(existing_stmt)).scalars().all()
        existing_by_label = {h.label: h for h in existing_rows}

        # 4) Para hashtags NUEVOS: filtro banned_terms con threshold 'low'.
        new_labels = [l for l in normalized if l not in existing_by_label]
        for label in new_labels:
            banned = await banned_terms_filter(self.db, label, severity_threshold="low")
            if banned:
                raise HashtagBannedTermsError(label=label, term=banned)

        # 5) Insertar nuevos.
        for label in new_labels:
            h = Hashtag(label=label, usage_count=1, created_by_id=created_by_id)
            self.db.add(h)
            existing_by_label[label] = h
        await self.db.flush()

        # 6) Incrementar usage_count de los que YA existian (no de los nuevos: ya van con 1).
        for label in normalized:
            if label in existing_by_label and label not in new_labels:
                existing_by_label[label].usage_count += 1
        await self.db.flush()

        return [existing_by_label[l] for l in normalized]

    async def autocomplete(
        self,
        *,
        prefix: str,
        limit: int = 10,
    ) -> list[HashtagSuggestion]:
        prefix = (prefix or "").strip().lower()
        if not prefix:
            return []
        like = f"{escape_like(prefix)}%"
        stmt = (
            select(Hashtag.label, Hashtag.usage_count)
            .where(Hashtag.label.ilike(like, escape="\\"))
            .order_by(Hashtag.usage_count.desc(), Hashtag.label.asc())
            .limit(limit)
        )
        rows = (await self.db.execute(stmt)).all()
        return [HashtagSuggestion(label=r.label, usage_count=r.usage_count) for r in rows]
