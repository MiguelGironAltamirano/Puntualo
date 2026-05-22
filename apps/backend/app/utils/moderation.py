"""app/utils/moderation.py

Filtro heuristico de terminos prohibidos (RF-15). Lee de la tabla `banned_terms`
con cache en memoria de 60s (refresco perezoso por TTL local). Sin Redis para
evitar otra dependencia; el cache es por-proceso y se invalida cuando expira.

Para hashtags: usar severity_threshold='low' (mas estricto).
Para comentarios: usar severity_threshold='medium'.
"""
from __future__ import annotations

import time
import unicodedata
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.banned_term import BannedTerm

Severity = Literal["low", "medium", "high"]

_SEVERITY_RANK: dict[str, int] = {"low": 1, "medium": 2, "high": 3}

_CACHE_TTL_SECONDS = 60
_cache: dict[str, list[tuple[str, str]]] = {"all": []}
_cache_loaded_at: float = 0.0


def _reset_cache_for_tests() -> None:
    """Helper que usan los tests; no usar en codigo de produccion."""
    global _cache_loaded_at
    _cache["all"] = []
    _cache_loaded_at = 0.0


def _strip_diacritics(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


async def _load_terms(db: AsyncSession) -> list[tuple[str, str]]:
    """Devuelve [(term_normalized, severity), ...]."""
    global _cache_loaded_at
    now = time.monotonic()
    if _cache["all"] and (now - _cache_loaded_at) < _CACHE_TTL_SECONDS:
        return _cache["all"]

    stmt = select(BannedTerm.term, BannedTerm.severity)
    rows = (await db.execute(stmt)).all()
    normalized = [
        (_strip_diacritics(t).lower(), s)
        for (t, s) in rows
    ]
    _cache["all"] = normalized
    _cache_loaded_at = now
    return normalized


async def banned_terms_filter(
    db: AsyncSession,
    text: str,
    *,
    severity_threshold: Severity = "medium",
) -> str | None:
    """Devuelve el primer termino prohibido detectado (>= threshold) o None.

    El match es substring sobre el texto normalizado (lowercase + sin diacriticos).
    No usa word-boundary porque hashtags y palabras concatenadas son comunes.
    """
    if not text:
        return None

    haystack = _strip_diacritics(text).lower()
    min_rank = _SEVERITY_RANK[severity_threshold]
    terms = await _load_terms(db)
    for term, sev in terms:
        if _SEVERITY_RANK.get(sev, 0) < min_rank:
            continue
        if term and term in haystack:
            return term
    return None
