from datetime import datetime

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


VALIDATION_STATUSES = {"pending_validation", "validated", "rejected"}


class ProfessorCreate(BaseModel):

    full_name: str = Field(min_length=3, max_length=200)

    university: str = Field(min_length=2, max_length=150)

    faculty: str = Field(min_length=2, max_length=150)


class ProfessorUpdate(BaseModel):

    full_name: str | None = Field(default=None, min_length=3, max_length=200)

    university: str | None = Field(default=None, min_length=2, max_length=150)

    faculty: str | None = Field(default=None, min_length=2, max_length=150)

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

    model_config = {
        "from_attributes": True
    }


class PaginatedProfessors(BaseModel):

    items: list[ProfessorOut]

    total: int

    page: int

    page_size: int

    total_pages: int

    has_next: bool

    has_prev: bool
