from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.services.professor_validation.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

# Tipo de los registros de evidencia que retorna pipeline.run()
EvidenceRecord = dict  # {source, role, found, affiliation_confirmed, confidence, payload}


class ProfessorValidationPipeline:
    """
    Orquesta sources en dos fases:
    - Fase 1 Validación: corte temprano en cuanto una fuente confirma afiliación.
    - Fase 2 Enrichment: todas las fuentes en paralelo, sin corte temprano.
    """

    def __init__(self, sources: list, budget: Any = None) -> None:
        self._validation_sources = sorted(
            [s for s in sources if s.role in ("validation", "both")],
            key=lambda s: s.priority,
        )
        self._enrichment_sources = sorted(
            [s for s in sources if s.role in ("enrichment", "both")],
            key=lambda s: s.priority,
        )
        self._budget = budget
        self._cb = CircuitBreaker()

    async def run(self, professor: Any) -> tuple[str, list[EvidenceRecord]]:
        evidence_records: list[EvidenceRecord] = []

        # ------------------------------------------------------------------
        # Fase 1 — Validación (corte temprano)
        # ------------------------------------------------------------------
        affiliation_confirmed = False

        for source in self._validation_sources:
            if await self._cb.is_open(source.name):
                logger.info("circuit open | source=%s, skipping validation", source.name)
                continue
            try:
                result = await source.validate(professor.full_name)
                evidence_records.append({
                    "source": source.name,
                    "role": "validation",
                    "found": result.found,
                    "affiliation_confirmed": result.affiliation_confirmed,
                    "confidence": result.confidence,
                    "payload": result.evidence,
                })
                if result.affiliation_confirmed:
                    affiliation_confirmed = True
                    break
            except Exception as exc:
                await self._cb.register_failure(source.name)
                logger.warning("validation source failed | source=%s | error=%s", source.name, exc)

        if not affiliation_confirmed:
            return "not_found", evidence_records

        # ------------------------------------------------------------------
        # Fase 2 — Enrichment (paralelo)
        # Hints iniciales: extraídos de la evidencia de la fase de validación.
        # ------------------------------------------------------------------
        initial_hints: dict = {}
        for rec in evidence_records:
            if rec["role"] == "validation" and rec["payload"]:
                for k, v in rec["payload"].items():
                    if k not in initial_hints:
                        initial_hints[k] = v

        enrichment_results = await asyncio.gather(
            *[self._run_enrichment(source, professor.full_name, initial_hints)
              for source in self._enrichment_sources],
            return_exceptions=True,
        )

        for item in enrichment_results:
            if item is not None and not isinstance(item, BaseException):
                evidence_records.append(item)

        return "validated", evidence_records

    async def _run_enrichment(
        self,
        source: Any,
        full_name: str,
        hints: dict,
    ) -> EvidenceRecord | None:
        if await self._cb.is_open(source.name):
            logger.info("circuit open | source=%s, skipping enrichment", source.name)
            return None

        if source.cost_per_call > 0 and self._budget is not None:
            if not await self._budget.try_consume(source.cost_per_call):
                logger.warning("budget exhausted | source=%s, skipping", source.name)
                return None

        try:
            result = await source.enrich(full_name, hints=hints)
            return {
                "source": source.name,
                "role": "enrichment",
                "found": bool(result.fields),
                "affiliation_confirmed": False,
                "confidence": None,
                "payload": result.fields,
            }
        except Exception as exc:
            await self._cb.register_failure(source.name)
            logger.warning("enrichment source failed | source=%s | error=%s", source.name, exc)
            return None
