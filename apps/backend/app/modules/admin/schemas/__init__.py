"""Admin schemas module."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AdminStatsResponse(BaseModel):
    users_pending: int
    professors_pending: int


# ── Verification admin schemas ─────────────────────────────────────────────────

class DocumentInfo(BaseModel):
    id: uuid.UUID
    side: Optional[str]
    file_path: str
    mime_type: str


class PendingVerificationItem(BaseModel):
    request_id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    email: str
    username: str
    dni: Optional[str]
    career_name: Optional[str]
    documents: list[DocumentInfo]
    submitted_at: datetime


class PendingVerificationsResponse(BaseModel):
    total: int
    items: list[PendingVerificationItem]


class RejectVerificationRequest(BaseModel):
    reason: str


# ── Professor validation admin schemas ────────────────────────────────────────

class EvidenceInfo(BaseModel):
    source: str
    role: str
    found: bool
    affiliation_confirmed: bool
    confidence: Optional[float]


class PendingProfessorItem(BaseModel):
    professor_id: uuid.UUID
    full_name: str
    university_name: str
    faculty_name: str
    validation_status: str
    global_score: Optional[float]
    total_evaluations: int
    registered_at: datetime
    evidence: list[EvidenceInfo]


class PendingProfessorsResponse(BaseModel):
    total: int
    items: list[PendingProfessorItem]
