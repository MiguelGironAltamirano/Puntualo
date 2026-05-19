"""Schemas Pydantic del modulo evaluations."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Course (Tarea 5)
# ---------------------------------------------------------------------------

class CourseCreate(BaseModel):
    """Payload para `POST /courses` (find-or-create)."""

    name: str = Field(..., min_length=1, max_length=150)
    university_id: int = Field(..., gt=0)
    faculty_id: int = Field(..., gt=0)


class CourseRead(BaseModel):
    """Shape publico de Course en respuestas."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    university_id: int
    faculty_id: int
    is_active: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# Evaluation (Tarea 6)
# ---------------------------------------------------------------------------

Modality = Literal["virtual", "presencial", "ambas"]


class EvaluationCreate(BaseModel):
    """Payload de `POST /evaluations`. `comment_text` es opcional (1:1 con Eval)."""

    professor_id: str = Field(..., min_length=1)
    course_id: str = Field(..., min_length=1)
    clarity: int = Field(..., ge=1, le=5)
    easiness: int = Field(..., ge=1, le=5)
    helpfulness: int = Field(..., ge=1, le=5)
    punctuality: int = Field(..., ge=1, le=5)
    course_difficulty: int = Field(..., ge=1, le=5)
    modality: Modality
    comment_text: str | None = Field(default=None, max_length=2000)


class CommentEmbedded(BaseModel):
    """Comentario incrustado en la respuesta de crear evaluacion."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    text: str | None
    modality: str
    is_verified: bool
    status: str
    helpful_count: int
    not_helpful_count: int
    created_at: datetime


class ProfessorScoreSnapshot(BaseModel):
    """Snapshot del score del profesor tras el recalculo."""

    professor_id: str
    global_score: float | None
    total_evaluations: int


class EvaluationRead(BaseModel):
    """Respuesta de crear evaluacion: evaluation + comment? + score snapshot."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    professor_id: str
    course_id: str
    semester: str
    clarity: int
    easiness: int
    helpfulness: int
    punctuality: int
    course_difficulty: int
    modality: str
    created_at: datetime

    comment: CommentEmbedded | None = None
    professor_score: ProfessorScoreSnapshot | None = None


# ---------------------------------------------------------------------------
# Comment (Tarea 7) — shape publico (sin user_id, status, reports_count, etc.)
# ---------------------------------------------------------------------------

class CommentRead(BaseModel):
    """Shape publico de Comment. Solo se sirven items `status='published'`."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    professor_id: str
    course_id: str
    text: str | None
    modality: str
    is_verified: bool
    helpful_count: int
    not_helpful_count: int
    created_at: datetime


__all__ = [
    "BaseModel",
    "CommentEmbedded",
    "CommentRead",
    "ConfigDict",
    "CourseCreate",
    "CourseRead",
    "EvaluationCreate",
    "EvaluationRead",
    "Field",
    "Modality",
    "ProfessorScoreSnapshot",
    "datetime",
]
