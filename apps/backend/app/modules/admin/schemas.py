import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AdminStatsResponse(BaseModel):

    users_pending: int

    professors_pending: int


# ── Verification admin schemas ─────────────────────────────────────────────────

class DocumentInfo(BaseModel):
    """Imagen de un lado del carnet (front o back)."""

    id: uuid.UUID
    side: Optional[str]       # "front" | "back" | None
    file_path: str            # URL pública de Supabase
    mime_type: str


class PendingVerificationItem(BaseModel):
    """Fila de la tabla de verificaciones pendientes."""

    request_id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    email: str
    username: str
    dni: Optional[str]
    career_name: Optional[str]
    documents: list[DocumentInfo]   # máx. 2 (front + back)
    submitted_at: datetime          # created_at del VerificationRequest


class PendingVerificationsResponse(BaseModel):
    total: int
    items: list[PendingVerificationItem]


class RejectVerificationRequest(BaseModel):
    """Body del endpoint de rechazo."""

    reason: str   # uno de los motivos preestablecidos


# ── Professor validation admin schemas ────────────────────────────────────────

class EvidenceInfo(BaseModel):
    """Resumen de una fuente de evidencia para el modal de detalle."""

    source: str                          # "unmsm_directory" | "openalex" | "orcid" | "tavily"
    role: str                            # "primary" | "enrichment"
    found: bool
    affiliation_confirmed: bool
    confidence: Optional[float]


class PendingProfessorItem(BaseModel):
    """Tarjeta de un profesor pendiente de validación manual."""

    professor_id: uuid.UUID
    full_name: str
    university_name: str
    faculty_name: str
    validation_status: str
    global_score: Optional[float]
    total_evaluations: int
    registered_at: datetime              # created_at del Professor
    evidence: list[EvidenceInfo]         # resultados de fuentes de IA


class PendingProfessorsResponse(BaseModel):
    total: int
    items: list[PendingProfessorItem]
