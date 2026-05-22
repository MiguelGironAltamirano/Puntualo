from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Literal
from urllib.parse import quote

import httpx

from app.core.config import settings
from app.services.professor_validation.sources.base import (
    EnrichmentResult,
    FieldWithProvenance,
    ValidationResult,
)
import app.utils.cache as _cache_mod

logger = logging.getLogger(__name__)

_BASE = settings.OPENALEX_API_BASE
_INST_ID = settings.OPENALEX_INSTITUTION_ID


def _make_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(
            settings.PIPELINE_TIMEOUT_READ,
            connect=settings.PIPELINE_TIMEOUT_CONNECT,
        ),
        headers={"User-Agent": settings.OPENALEX_USER_AGENT},
        follow_redirects=True,
    )


def _extract_orcid_id(orcid_url: str | None) -> str:
    """'https://orcid.org/0000-0001-2345-6789' → '0000-0001-2345-6789'"""
    if not orcid_url:
        return ""
    return orcid_url.rstrip("/").split("/")[-1]


def _extract_author_id(openalex_url: str) -> str:
    """'https://openalex.org/A1234567890' → 'A1234567890'"""
    return openalex_url.rstrip("/").split("/")[-1]


def _top_concepts(results_item: dict, n: int = 5) -> list[str]:
    return [c["display_name"] for c in results_item.get("x_concepts", [])[:n]]


def _affiliation_years(results_item: dict) -> list[int]:
    for aff in results_item.get("affiliations", []):
        inst = aff.get("institution", {})
        # compare by ID, never by display_name (OpenAlex normaliza imperfectamente)
        if _INST_ID in inst.get("id", ""):
            return aff.get("years", [])
    return []


class OpenAlexSource:
    name: str = "openalex"
    role: Literal["validation", "enrichment", "both"] = "both"
    priority: int = 2
    cost_per_call: int = 0

    # ------------------------------------------------------------------
    # validate
    # ------------------------------------------------------------------

    async def validate(self, full_name: str) -> ValidationResult:
        cache_key = f"openalex:validate:{full_name}"
        cached = await _cache_mod.redis_client.get(cache_key)
        if cached:
            return ValidationResult.model_validate_json(cached)

        # ⚠️ CRÍTICO: usar affiliations.institution.id, NO last_known_institutions.id
        url = (
            f"{_BASE}/authors"
            f"?search={quote(full_name)}"
            f"&filter=affiliations.institution.id:{_INST_ID}"
            f"&sort=works_count:desc"
            f"&per-page=5"
        )

        async with _make_client() as client:
            response = await client.get(url)
            response.raise_for_status()

        data = response.json()
        results = data.get("results", [])
        count = data.get("meta", {}).get("count", 0)

        if count == 0 or not results:
            result = ValidationResult(
                found=False,
                affiliation_confirmed=False,
                source=self.name,
                confidence=0.0,
                evidence={"meta_count": 0},
            )
            await _cache_mod.redis_client.set(cache_key, result.model_dump_json(), ex=settings.CACHE_TTL_VALIDATION_SECONDS)
            return result

        principal = results[0]
        evidence: dict = {
            "meta_count": count,
            "author_id": _extract_author_id(principal.get("id", "")),
            "display_name": principal.get("display_name", ""),
            "orcid": _extract_orcid_id(principal.get("orcid")),
            "works_count": principal.get("works_count", 0),
            "cited_by_count": principal.get("cited_by_count", 0),
            "top_concepts": _top_concepts(principal),
            "affiliation_years": _affiliation_years(principal),
        }

        if len(results) >= 2:
            top1 = principal.get("works_count", 0) or 0
            top2 = results[1].get("works_count", 0) or 0
            if top1 > 0 and top2 / top1 > 0.5:
                evidence["validation_with_ambiguity"] = True

        result = ValidationResult(
            found=True,
            affiliation_confirmed=True,
            source=self.name,
            confidence=0.9,
            evidence=evidence,
        )
        await _cache_mod.redis_client.set(cache_key, result.model_dump_json(), ex=settings.CACHE_TTL_VALIDATION_SECONDS)
        return result

    # ------------------------------------------------------------------
    # enrich
    # ------------------------------------------------------------------

    async def enrich(self, full_name: str, hints: dict) -> EnrichmentResult:
        author_data = await self._fetch_author(full_name, hints)
        if not author_data:
            return EnrichmentResult(fields={}, source=self.name)

        now = datetime.now(timezone.utc)
        fields: dict[str, FieldWithProvenance] = {}

        def _field(key: str, value: object) -> None:
            if value:
                fields[key] = FieldWithProvenance(
                    value=value,
                    source=self.name,
                    fetched_at=now,
                    confidence=0.9,
                )

        _field("works_count", author_data.get("works_count"))
        _field("cited_by_count", author_data.get("cited_by_count"))
        _field("top_concepts", _top_concepts(author_data))
        _field("affiliation_years_unmsm", _affiliation_years(author_data))
        _field("orcid", _extract_orcid_id(author_data.get("orcid")))
        _field("openalex_id", _extract_author_id(author_data.get("id", "")))

        return EnrichmentResult(fields=fields, source=self.name)

    async def _fetch_author(self, full_name: str, hints: dict) -> dict | None:
        # Preferir ORCID de hints (mayor precisión)
        orcid_hint = hints.get("orcid")
        if orcid_hint:
            orcid_id = orcid_hint.value if hasattr(orcid_hint, "value") else str(orcid_hint)
            if orcid_id:
                return await self._fetch_by_orcid(orcid_id)

        # Intentar con author_id de hints (de una validación previa de este mismo source)
        author_id_hint = hints.get("openalex_id")
        if author_id_hint:
            aid = author_id_hint.value if hasattr(author_id_hint, "value") else str(author_id_hint)
            if aid:
                return await self._fetch_by_author_id(aid)

        # Fallback: buscar por nombre y tomar el principal
        return await self._fetch_by_name(full_name)

    async def _fetch_by_orcid(self, orcid_id: str) -> dict | None:
        cache_key = f"openalex:author:orcid:{orcid_id}"
        return await self._cached_author_fetch(cache_key, f"{_BASE}/authors/orcid:{orcid_id}")

    async def _fetch_by_author_id(self, author_id: str) -> dict | None:
        cache_key = f"openalex:author:id:{author_id}"
        return await self._cached_author_fetch(cache_key, f"{_BASE}/authors/{author_id}")

    async def _fetch_by_name(self, full_name: str) -> dict | None:
        url = (
            f"{_BASE}/authors"
            f"?search={quote(full_name)}"
            f"&filter=affiliations.institution.id:{_INST_ID}"
            f"&sort=works_count:desc"
            f"&per-page=1"
        )
        cache_key = f"openalex:author:name:{full_name}"
        cached = await _cache_mod.redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            return data[0] if data else None

        async with _make_client() as client:
            response = await client.get(url)
            response.raise_for_status()

        results = response.json().get("results", [])
        await _cache_mod.redis_client.set(cache_key, json.dumps(results[:1]), ex=settings.CACHE_TTL_ENRICHMENT_SECONDS)
        return results[0] if results else None

    async def _cached_author_fetch(self, cache_key: str, url: str) -> dict | None:
        cached = await _cache_mod.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        async with _make_client() as client:
            response = await client.get(url)
            if response.status_code == 404:
                return None
            response.raise_for_status()

        data = response.json()
        await _cache_mod.redis_client.set(cache_key, json.dumps(data), ex=settings.CACHE_TTL_ENRICHMENT_SECONDS)
        return data
