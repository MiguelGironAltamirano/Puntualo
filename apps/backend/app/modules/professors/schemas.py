from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.pagination import PaginatedResponse


VALIDATION_STATUSES = {"pending_validation", "validated", "rejected", "not_found"}


class ProfessorCreate(BaseModel):

    full_name: str = Field(min_length=3, max_length=200)

    university_id: int = Field(gt=0)

    faculty_id: int = Field(gt=0)


class ProfessorUpdate(BaseModel):

    full_name: str | None = Field(default=None, min_length=3, max_length=200)

    university_id: int | None = Field(default=None, gt=0)

    faculty_id: int | None = Field(default=None, gt=0)

    # TODO(2.4): restringir a rol admin cuando se implemente RBAC + integración SUNEDU.
    validation_status: str | None = None


class ProfessorOut(BaseModel):

    id: str

    full_name: str

    university_id: int

    faculty_id: int

    validation_status: str

    registered_by_id: str | None = None

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = {"from_attributes": True}


PaginatedProfessors = PaginatedResponse[ProfessorOut]


class RevalidateResponse(BaseModel):
    queued: bool
    professor_id: str
