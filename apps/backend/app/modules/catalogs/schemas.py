from pydantic import BaseModel


class UniversityOut(BaseModel):
    id: int
    name: str
    city: str
    country: str

    model_config = {"from_attributes": True}


class FacultyOut(BaseModel):
    id: int
    university_id: int
    name: str

    model_config = {"from_attributes": True}
