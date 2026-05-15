from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.pagination import PaginatedResponse


VALIDATION_STATUSES = {"pending_validation", "validated", "rejected"}


class ProfessorCreate(BaseModel):

    full_name: str = Field(min_length=3, max_length=200)

    university: str = Field(min_length=2, max_length=150)

    faculty: str = Field(min_length=2, max_length=150)


class ProfessorUpdate(BaseModel):

    full_name: str | None = Field(default=None, min_length=3, max_length=200)

    university: str | None = Field(default=None, min_length=2, max_length=150)

    faculty: str | None = Field(default=None, min_length=2, max_length=150)

    # TODO(2.4): restringir a rol admin cuando se implemente RBAC + integración SUNEDU.
    validation_status: str | None = None


class ProfessorOut(BaseModel):

    id: str

    full_name: str

    university: str

    faculty: str

    validation_status: str

    registered_by_id: str | None = None

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = {"from_attributes": True}


PaginatedProfessors = PaginatedResponse[ProfessorOut]
