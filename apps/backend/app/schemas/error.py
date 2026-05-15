from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., json_schema_extra={"example": "PROFESSOR_NOT_FOUND"})
    message: str = Field(..., json_schema_extra={"example": "Profesor no encontrado"})


class ErrorResponse(BaseModel):
    detail: ErrorDetail
