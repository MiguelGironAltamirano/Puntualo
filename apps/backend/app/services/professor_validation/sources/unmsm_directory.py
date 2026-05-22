from __future__ import annotations

import asyncio
import json
import logging
import unicodedata
from datetime import datetime, timezone
from typing import Literal

import httpx
from bs4 import BeautifulSoup

from app.core.config import settings
from app.services.professor_validation.sources.base import (
    EnrichmentResult,
    FieldWithProvenance,
    ValidationResult,
)
import app.utils.cache as _cache_mod

logger = logging.getLogger(__name__)

_ACADEMIC_PREFIXES = {"dr.", "mg.", "mtro.", "lic.", "ing.", "dr", "mg", "mtro", "lic", "ing"}

_URL_TO_DEPARTMENT = {
    "directorio-dacc": "DACC — Ciencias de la Computación",
    "directorio-daisw": "DAISW — Ingeniería de Software",
    "posgrado/docentes": "Posgrado FISI",
}


def _normalize_tokens(name: str) -> list[str]:
    name = name.replace(",", " ")
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = name.lower()
    return [t for t in name.split() if t not in _ACADEMIC_PREFIXES]


def _infer_department(url: str) -> str:
    for fragment, dept in _URL_TO_DEPARTMENT.items():
        if fragment in url:
            return dept
    return ""


def _parse_last_semester_table(html: str, url: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        return []

    last_table = tables[-1]
    department = _infer_department(url)
    professors = []

    for row in last_table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 7:
            continue

        raw_name = cells[1].get_text(separator=" ", strip=True)
        if not raw_name or raw_name.upper() in ("APELLIDOS Y NOMBRES", "NRO"):
            continue

        cat = cells[2].get_text(strip=True)
        clase = cells[3].get_text(strip=True)

        cv_link = cells[4].find("a")
        cv_pdf_url = ""
        if cv_link and cv_link.get("href"):
            href = cv_link["href"]
            base = settings.UNMSM_DIRECTORY_URLS[0].split("/site/")[0]
            cv_pdf_url = href if href.startswith("http") else base + href

        professors.append({
            "raw_name": raw_name,
            "normalized_tokens": sorted(_normalize_tokens(raw_name)),
            "categoria": cat,
            "dedicacion": clase,
            "departamento": department,
            "cv_pdf_url": cv_pdf_url,
            "email_institucional": "",  # JS-obfuscated in static HTML
        })

    return professors


class UnmsmDirectorySource:
    name: str = "unmsm_directory"
    role: Literal["validation", "enrichment", "both"] = "both"
    priority: int = 1
    cost_per_call: int = 0

    async def _fetch_url(self, client: httpx.AsyncClient, url: str) -> list[dict]:
        cache_key = f"unmsm_directory:parsed:{url}"
        cached = await _cache_mod.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        response = await client.get(url)
        response.raise_for_status()

        professors = _parse_last_semester_table(response.text, url)
        await _cache_mod.redis_client.set(
            cache_key,
            json.dumps(professors, ensure_ascii=False),
            ex=settings.CACHE_TTL_VALIDATION_SECONDS,
        )
        return professors

    async def _get_all_professors(self) -> list[dict]:
        timeout = httpx.Timeout(
            settings.PIPELINE_TIMEOUT_READ,
            connect=settings.PIPELINE_TIMEOUT_CONNECT,
        )
        headers = {"User-Agent": settings.UNMSM_USER_AGENT}
        all_professors: list[dict] = []

        async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
            for i, url in enumerate(settings.UNMSM_DIRECTORY_URLS):
                if i > 0:
                    await asyncio.sleep(settings.UNMSM_RATE_LIMIT_SECONDS)
                try:
                    profs = await self._fetch_url(client, url)
                    all_professors.extend(profs)
                except Exception as e:
                    logger.warning(f"unmsm_directory: failed to fetch {url}: {e}")

        return all_professors

    def _find_match(self, professors: list[dict], full_name: str) -> dict | None:
        input_tokens = sorted(_normalize_tokens(full_name))
        for prof in professors:
            if prof["normalized_tokens"] == input_tokens:
                return prof
        return None

    async def validate(self, full_name: str) -> ValidationResult:
        professors = await self._get_all_professors()
        match = self._find_match(professors, full_name)

        if match:
            return ValidationResult(
                found=True,
                affiliation_confirmed=True,
                source=self.name,
                confidence=0.95,
                evidence=match,
            )

        return ValidationResult(
            found=False,
            affiliation_confirmed=False,
            source=self.name,
            confidence=0.0,
            evidence={},
        )

    async def enrich(self, full_name: str, hints: dict) -> EnrichmentResult:
        professors = await self._get_all_professors()
        match = self._find_match(professors, full_name)

        if not match:
            return EnrichmentResult(fields={}, source=self.name)

        now = datetime.now(timezone.utc)
        fields: dict[str, FieldWithProvenance] = {}
        for field in ("categoria", "dedicacion", "departamento", "cv_pdf_url", "email_institucional"):
            value = match.get(field, "")
            if value:
                fields[field] = FieldWithProvenance(
                    value=value,
                    source=self.name,
                    fetched_at=now,
                    confidence=0.95,
                )

        return EnrichmentResult(fields=fields, source=self.name)
