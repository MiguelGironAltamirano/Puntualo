import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, computed_field, field_validator

from app.schemas.pagination import PaginatedResponse


VALIDATION_STATUSES = {"pending_validation", "validated", "not_found", "rejected"}

SortField = Literal["created_at", "global_score", "total_evaluations"]
SortOrder = Literal["asc", "desc"]


class ProfessorCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=200)
    university_id: int = Field(gt=0)
    faculty_id: int = Field(gt=0)
    course_ids: list[int] = Field(min_length=1, max_length=10)


class ProfessorUpdate(BaseModel):
    model_config = {"extra": "forbid"}

    full_name: str | None = Field(default=None, min_length=3, max_length=200)
    university_id: int | None = Field(default=None, gt=0)
    faculty_id: int | None = Field(default=None, gt=0)


class _ProfessorBase(BaseModel):
    id: str
    full_name: str
    university_id: int
    faculty_id: int
    validation_status: str
    global_score: float | None = None
    total_evaluations: int = 0
    avg_clarity: float | None = None
    avg_easiness: float | None = None
    avg_helpfulness: float | None = None
    avg_punctuality: float | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def _coerce_uuid_id(cls, v):
        return str(v) if isinstance(v, uuid.UUID) else v

    @computed_field
    @property
    def is_provisional(self) -> bool:
        return self.validation_status == "pending_validation"


class ProfessorOut(_ProfessorBase):
    """Respuesta pública: oculta registered_by_id por anonimato."""
    pass


class ProfessorAdminOut(_ProfessorBase):
    """Respuesta admin: incluye registered_by_id y deleted_at para auditoría."""
    registered_by_id: str | None = None
    deleted_at: datetime | None = None

    @field_validator("registered_by_id", mode="before")
    @classmethod
    def _coerce_uuid_registered_by(cls, v):
        return str(v) if isinstance(v, uuid.UUID) else v


class CourseRef(BaseModel):
    id: int
    name: str
    faculty_id: int

    model_config = {"from_attributes": True}


class DegreeRef(BaseModel):
    id: int
    name: str
    level: str
    institution: str | None = None
    year_obtained: int | None = None


class EvidenceRef(BaseModel):
    source: str
    role: str
    affiliation_confirmed: bool
    confidence: float | None = None
    fetched_at: datetime

    model_config = {"from_attributes": True}


class AiSummaryOut(BaseModel):
    summary: str
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    model_version: str
    generated_at: datetime

    model_config = {"from_attributes": True}


class ProfessorDetail(_ProfessorBase):
    university_name: str | None = None
    faculty_name: str | None = None
    courses: list[CourseRef] = Field(default_factory=list)
    degrees: list[DegreeRef] = Field(default_factory=list)
    evidence: list[EvidenceRef] = Field(default_factory=list)
    executive_summary: str | None = None
    ai_summary: AiSummaryOut | None = None
    ai_summary_reason: str | None = None


class ProfessorDetailAdmin(ProfessorDetail):
    registered_by_id: str | None = None
    deleted_at: datetime | None = None


class ProfessorCourseAdd(BaseModel):
    course_id: int = Field(gt=0)


class RevalidateResponse(BaseModel):
    queued: bool
    professor_id: str


class RejectResponse(BaseModel):
    professor_id: str
    validation_status: str


PaginatedProfessors = PaginatedResponse[ProfessorOut]
PaginatedProfessorsAdmin = PaginatedResponse[ProfessorAdminOut]
