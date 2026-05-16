from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Literal

import httpx

from app.core.config import settings
from app.services.professor_validation.budget import BudgetTracker
from app.services.professor_validation.pipeline import (
    EnrichmentResult,
    FieldWithProvenance,
    ValidationResult,
)

logger = logging.getLogger(__name__)

# Campos que Tavily intenta completar; si todos están presentes, se salta.
_TRIGGER_FIELDS = frozenset({"photo_url", "bio_narrative", "external_links"})


def _make_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(
            settings.PIPELINE_TIMEOUT_READ,
            connect=settings.PIPELINE_TIMEOUT_CONNECT,
        ),
        follow_redirects=True,
    )


class TavilySource:
    """
    Enrichment fallback (tier 4). NUNCA validation.
    Solo se ejecuta si los enrichers anteriores dejaron campos clave vacíos.
    Cada call consume 1 unidad del BudgetTracker.
    """

    name: str = "tavily"
    role: Literal["enrichment"] = "enrichment"
    priority: int = 4
    cost_per_call: int = 1

    def __init__(self, budget: BudgetTracker | None = None) -> None:
        self._budget = budget

    async def validate(self, full_name: str) -> ValidationResult:
        # Tavily nunca valida — siempre retorna not-confirmed
        return ValidationResult(
            found=False,
            affiliation_confirmed=False,
            source=self.name,
            confidence=0.0,
            evidence={},
        )

    async def enrich(self, full_name: str, hints: dict) -> EnrichmentResult:
        # Trigger condicional: ejecutar solo si falta al menos un campo clave
        missing = _TRIGGER_FIELDS - set(hints.keys())
        if not missing:
            logger.debug(f"tavily: all trigger fields present for '{full_name}', skipping")
            return EnrichmentResult(fields={}, source=self.name)

        # Verificar budget antes de hacer la llamada
        if self._budget is not None and not await self._budget.try_consume(1):
            logger.warning("tavily: budget exhausted, skipping enrichment")
            return EnrichmentResult(fields={}, source=self.name)

        query = f"{full_name} UNMSM profesor"
        search_results = await self._search(query)

        if not search_results:
            return EnrichmentResult(fields={}, source=self.name)

        # Intentar extract sobre la URL más prometedora
        best_url = search_results[0].get("url", "")
        extracted_content = ""
        if best_url and self._budget is not None:
            if await self._budget.try_consume(1):
                extracted_content = await self._extract(best_url)
        elif best_url and self._budget is None:
            extracted_content = await self._extract(best_url)

        now = datetime.now(timezone.utc)
        fields: dict[str, FieldWithProvenance] = {}

        external_links = [r.get("url", "") for r in search_results if r.get("url")]
        if external_links:
            fields["external_links"] = FieldWithProvenance(
                value=external_links,
                source=self.name,
                fetched_at=now,
                confidence=0.6,
            )

        if extracted_content:
            fields["bio_narrative"] = FieldWithProvenance(
                value=extracted_content[:2000],
                source=self.name,
                fetched_at=now,
                confidence=0.5,
            )

        return EnrichmentResult(fields=fields, source=self.name)

    async def _search(self, query: str) -> list[dict]:
        payload = {
            "api_key": settings.TAVILY_API_KEY,
            "query": query,
            "max_results": 5,
            "search_depth": "basic",
        }
        try:
            async with _make_client() as client:
                response = await client.post(
                    f"{settings.TAVILY_API_BASE}/search",
                    json=payload,
                )
                response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            logger.warning(f"tavily: search failed for query '{query}': {e}")
            return []

    async def _extract(self, url: str) -> str:
        """
        Extrae contenido de una URL. Tasa de fallo ~50% — se trata como skip graceful.
        """
        payload = {
            "api_key": settings.TAVILY_API_KEY,
            "urls": [url],
        }
        try:
            async with _make_client() as client:
                response = await client.post(
                    f"{settings.TAVILY_API_BASE}/extract",
                    json=payload,
                )
                response.raise_for_status()

            data = response.json()
            # failed_results[] es esperado (~50%); se ignora gracefully
            results = data.get("results", [])
            if results:
                return results[0].get("raw_content", "")
            return ""
        except Exception as e:
            logger.warning(f"tavily: extract failed for url '{url}': {e}")
            return ""
