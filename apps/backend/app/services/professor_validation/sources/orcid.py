from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Literal
from urllib.parse import quote

import httpx

from app.core.config import settings
from app.services.professor_validation.pipeline import (
    EnrichmentResult,
    FieldWithProvenance,
    ValidationResult,
)
import app.utils.cache as _cache_mod

logger = logging.getLogger(__name__)

_BASE = settings.ORCID_API_BASE
_UNMSM_ORG_VARIANTS = frozenset({
    "universidad nacional mayor de san marcos",
    "national university of san marcos",
    "unmsm",
    "universidad de san marcos",
})


def _make_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(
            settings.PIPELINE_TIMEOUT_READ,
            connect=settings.PIPELINE_TIMEOUT_CONNECT,
        ),
        headers={
            "Accept": "application/json",
            "User-Agent": settings.UNMSM_USER_AGENT,
        },
        follow_redirects=True,
    )


def _split_name(full_name: str) -> tuple[str, str]:
    """
    Para nombres españoles con 2 apellidos:
    'Ciro Rodriguez Rodriguez'      → ('Ciro', 'Rodriguez Rodriguez')
    'Lenis Rossi Wong Portillo'     → ('Lenis Rossi', 'Wong Portillo')
    'Adegundo Mario Camara Figueroa'→ ('Adegundo Mario', 'Camara Figueroa')
    """
    tokens = full_name.strip().split()
    if len(tokens) <= 1:
        return full_name, ""
    if len(tokens) == 2:
        return tokens[0], tokens[1]
    # Últimos 2 tokens = apellidos; el resto = nombres
    return " ".join(tokens[:-2]), " ".join(tokens[-2:])


def _extract_orcid_path(result_item: dict) -> str:
    return result_item.get("orcid-identifier", {}).get("path", "")


def _has_unmsm_employment(employments_section: dict) -> bool:
    for group in employments_section.get("affiliation-group", []):
        for summary in group.get("summaries", []):
            org_name = (
                summary.get("employment-summary", {})
                .get("organization", {})
                .get("name", "")
                .lower()
            )
            if any(variant in org_name for variant in _UNMSM_ORG_VARIANTS):
                return True
    return False


def _extract_employments(employments_section: dict) -> list[dict]:
    result = []
    for group in employments_section.get("affiliation-group", []):
        for summary in group.get("summaries", []):
            emp = summary.get("employment-summary", {})
            start = emp.get("start-date") or {}
            end = emp.get("end-date")
            result.append({
                "organization": emp.get("organization", {}).get("name", ""),
                "role": emp.get("role-title", ""),
                "start_year": start.get("year", {}).get("value"),
                "end_year": (end or {}).get("year", {}).get("value") if end else None,
            })
    return result


def _extract_works(works_section: dict, limit: int = 10) -> list[str]:
    titles = []
    for group in works_section.get("group", [])[:limit]:
        summaries = group.get("work-summary", [])
        if summaries:
            title_obj = summaries[0].get("title", {}).get("title", {})
            title = title_obj.get("value", "")
            if title:
                titles.append(title)
    return titles


def _extract_educations(educations_section: dict) -> list[dict]:
    result = []
    for group in educations_section.get("affiliation-group", []):
        for summary in group.get("summaries", []):
            edu = summary.get("education-summary", {})
            result.append({
                "organization": edu.get("organization", {}).get("name", ""),
                "role": edu.get("role-title", ""),
            })
    return result


class OrcidSource:
    name: str = "orcid"
    role: Literal["validation", "enrichment", "both"] = "both"
    priority: int = 3
    cost_per_call: int = 0

    # ------------------------------------------------------------------
    # validate
    # ------------------------------------------------------------------

    async def validate(self, full_name: str) -> ValidationResult:
        cache_key = f"orcid:validate:{full_name}"
        cached = await _cache_mod.redis_client.get(cache_key)
        if cached:
            return ValidationResult.model_validate_json(cached)

        orcid_id = await self._search_filtered(full_name)

        if not orcid_id:
            # Fallback: búsqueda amplia + validar employment manualmente
            logger.debug(f"orcid: filtered search returned 0 for '{full_name}', trying broad fallback")
            orcid_id = await self._search_broad_with_employment_check(full_name)

        if not orcid_id:
            result = ValidationResult(
                found=False,
                affiliation_confirmed=False,
                source=self.name,
                confidence=0.0,
                evidence={},
            )
            await _cache_mod.redis_client.set(cache_key, result.model_dump_json(), ex=settings.CACHE_TTL_VALIDATION_SECONDS)
            return result

        result = ValidationResult(
            found=True,
            affiliation_confirmed=True,
            source=self.name,
            confidence=0.95,
            evidence={"orcid": orcid_id},
        )
        await _cache_mod.redis_client.set(cache_key, result.model_dump_json(), ex=settings.CACHE_TTL_VALIDATION_SECONDS)
        return result

    async def _search_filtered(self, full_name: str) -> str:
        """Busca con filtro affiliation-org-name; retorna ORCID id o ''.

        Usa solo el primer token de cada parte del nombre: ORCID trata términos
        multi-palabra como OR (ej. 'Adegundo Mario' → Adegundo OR Mario), lo que
        causa falsos negativos para apellidos compuestos. El filtro de afiliación
        aporta la discriminación suficiente.
        """
        given, family = _split_name(full_name)
        given_tok = given.split()[0]
        family_tok = family.split()[0]
        query = (
            f"given-names:{quote(given_tok)}"
            f"+AND+family-name:{quote(family_tok)}"
            f'+AND+affiliation-org-name:"{quote(settings.ORCID_AFFILIATION_NAME)}"'
        )
        return await self._run_search(query, cache_prefix="orcid:search:filtered")

    async def _search_broad_with_employment_check(self, full_name: str) -> str:
        """
        Búsqueda amplia (sin filtro de afiliación) iterando hasta 5 candidatos.
        Valida manualmente cada uno contra employments[].organization.name.
        Cubre casos donde el org name en ORCID no coincide exactamente (ej. Adegundo Camara).
        Usa primer token de cada parte del nombre por la misma razón que _search_filtered.
        """
        given, family = _split_name(full_name)
        given_tok = given.split()[0]
        family_tok = family.split()[0]
        query = f"given-names:{quote(given_tok)}+AND+family-name:{quote(family_tok)}"

        url = f"{_BASE}/search?q={query}&rows=5"
        async with _make_client() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
            except Exception as exc:
                logger.warning(f"orcid: broad search failed: {exc}")
                return ""

        results = response.json().get("result") or []
        for item in results:
            candidate_id = _extract_orcid_path(item)
            if not candidate_id:
                continue
            record = await self._fetch_record(candidate_id)
            if not record:
                continue
            employments = record.get("activities-summary", {}).get("employments", {})
            if _has_unmsm_employment(employments):
                return candidate_id

        return ""

    async def _run_search(self, query: str, cache_prefix: str) -> str:
        cache_key = f"{cache_prefix}:{query}"
        cached = await _cache_mod.redis_client.get(cache_key)
        if cached:
            return cached

        url = f"{_BASE}/search?q={query}"
        async with _make_client() as client:
            response = await client.get(url)
            response.raise_for_status()

        data = response.json()
        results = data.get("result") or []
        orcid_id = _extract_orcid_path(results[0]) if results else ""

        await _cache_mod.redis_client.set(cache_key, orcid_id, ex=settings.CACHE_TTL_VALIDATION_SECONDS)
        return orcid_id

    # ------------------------------------------------------------------
    # enrich
    # ------------------------------------------------------------------

    async def enrich(self, full_name: str, hints: dict) -> EnrichmentResult:
        orcid_id = self._orcid_from_hints(hints)

        if not orcid_id:
            orcid_id = await self._search_filtered(full_name)
        if not orcid_id:
            orcid_id = await self._search_broad_with_employment_check(full_name)
        if not orcid_id:
            return EnrichmentResult(fields={}, source=self.name)

        record = await self._fetch_record(orcid_id)
        if not record:
            return EnrichmentResult(fields={}, source=self.name)

        return self._build_enrichment(record, orcid_id)

    def _orcid_from_hints(self, hints: dict) -> str:
        hint = hints.get("orcid")
        if not hint:
            return ""
        return hint.value if hasattr(hint, "value") else str(hint)

    def _build_enrichment(self, record: dict, orcid_id: str) -> EnrichmentResult:
        now = datetime.now(timezone.utc)
        activities = record.get("activities-summary", {})
        person = record.get("person", {})

        fields: dict[str, FieldWithProvenance] = {}

        def _field(key: str, value: object) -> None:
            if value:
                fields[key] = FieldWithProvenance(
                    value=value,
                    source=self.name,
                    fetched_at=now,
                    confidence=0.95,
                )

        _field("orcid", orcid_id)
        _field("employments", _extract_employments(activities.get("employments", {})))
        _field("works_titles", _extract_works(activities.get("works", {})))
        _field("educations", _extract_educations(activities.get("educations", {})))

        biography = person.get("biography", {}) or {}
        _field("biography", biography.get("content", ""))

        return EnrichmentResult(fields=fields, source=self.name)

    async def _fetch_record(self, orcid_id: str) -> dict | None:
        cache_key = f"orcid:record:{orcid_id}"
        cached = await _cache_mod.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        url = f"{_BASE}/{orcid_id}/record"
        async with _make_client() as client:
            response = await client.get(url)
            if response.status_code == 404:
                return None
            response.raise_for_status()

        data = response.json()
        await _cache_mod.redis_client.set(cache_key, json.dumps(data), ex=settings.CACHE_TTL_ENRICHMENT_SECONDS)
        return data
