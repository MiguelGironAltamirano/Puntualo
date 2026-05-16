from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

from app.core.config import settings
from app.utils.cache import redis_client

logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    found: bool
    affiliation_confirmed: bool
    source: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: dict


class FieldWithProvenance(BaseModel):
    value: Any
    source: str
    fetched_at: datetime
    confidence: float


class EnrichmentResult(BaseModel):
    fields: dict[str, FieldWithProvenance]
    source: str


class ProfessorSource(Protocol):
    name: str
    role: Literal["validation", "enrichment", "both"]
    priority: int
    cost_per_call: int

    async def validate(self, full_name: str) -> ValidationResult: ...
    async def enrich(self, full_name: str, hints: dict) -> EnrichmentResult: ...


class ProfessorValidationPipeline:
    """
    Orquesta sources en orden de prioridad.
    Fase validación: corta apenas un source confirma afiliación UNMSM.
    Fase enriquecimiento: ejecuta todos los enrichers restantes dentro de budget.
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

    async def run(self, professor: Any) -> tuple[str, list]:
        evidence_records: list = []
        affiliation_confirmed = False

        # Fase 1: validation chain con corte temprano
        for source in self._validation_sources:
            if await self._is_circuit_open(source.name):
                continue
            try:
                result = await source.validate(professor.full_name)
                evidence_records.append((source.name, result.evidence))
                if result.affiliation_confirmed:
                    affiliation_confirmed = True
                    break
            except Exception as e:
                await self._register_failure(source.name)
                logger.warning(f"validation source {source.name} failed: {e}")

        if not affiliation_confirmed:
            return "not_found", evidence_records

        # Fase 2: enrichment chain (no corta temprano)
        merged_fields: dict[str, FieldWithProvenance] = {}
        for source in self._enrichment_sources:
            if await self._is_circuit_open(source.name):
                continue
            if source.cost_per_call > 0 and self._budget is not None:
                if not await self._budget.try_consume(source.cost_per_call):
                    continue
            try:
                result = await source.enrich(professor.full_name, hints=merged_fields)
                evidence_records.append((source.name, result.fields))
                self._merge_with_provenance(merged_fields, result.fields)
            except Exception as e:
                await self._register_failure(source.name)
                logger.warning(f"enrichment source {source.name} failed: {e}")

        return "validated", evidence_records

    async def _is_circuit_open(self, source_name: str) -> bool:
        key = f"circuit:{source_name}:failures"
        value = await redis_client.get(key)
        if value is None:
            return False
        return int(value) >= settings.CIRCUIT_THRESHOLD

    async def _register_failure(self, source_name: str) -> None:
        key = f"circuit:{source_name}:failures"
        new_value = await redis_client.incr(key)
        if new_value == 1:
            await redis_client.expire(key, settings.CIRCUIT_RESET_SECONDS)

    def _merge_with_provenance(
        self,
        merged: dict[str, FieldWithProvenance],
        new_fields: dict[str, FieldWithProvenance],
    ) -> None:
        # Higher-priority sources (lower priority number) are processed first;
        # their fields are never overwritten by lower-priority sources.
        for field_name, field_value in new_fields.items():
            if field_name not in merged:
                merged[field_name] = field_value
