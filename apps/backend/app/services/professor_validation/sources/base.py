from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field


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


class EvidenceSource(Protocol):
    name: str
    role: Literal["validation", "enrichment", "both"]
    priority: int
    cost_per_call: int

    async def validate(self, full_name: str) -> ValidationResult: ...
    async def enrich(self, full_name: str, hints: dict) -> EnrichmentResult: ...
