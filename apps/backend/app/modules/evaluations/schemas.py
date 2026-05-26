"""Schemas Pydantic del modulo evaluations."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------

class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    university_id: int = Field(..., gt=0)
    faculty_id: int = Field(..., gt=0)


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    university_id: int
    faculty_id: int
    evaluation_count: int = 0
    created_at: datetime


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

Modality = Literal["virtual", "presencial", "ambas"]


class EvaluationCreate(BaseModel):
    """Payload de POST /evaluations. comment_text y hashtags son opcionales."""

    professor_id: str = Field(..., min_length=1)
    course_id: int = Field(..., gt=0)
    clarity: int = Field(..., ge=1, le=5)
    easiness: int = Field(..., ge=1, le=5)
    helpfulness: int = Field(..., ge=1, le=5)
    punctuality: int = Field(..., ge=1, le=5)
    modality: Modality
    comment_text: str | None = Field(default=None, max_length=2000)
    hashtags: list[str] = Field(default_factory=list, max_length=5)


class CommentEmbedded(BaseModel):
    """Comentario incrustado en la respuesta de crear evaluacion. SIN user_id."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    text: str | None
    modality: str
    status: str
    like_count: int
    dislike_count: int
    created_at: datetime


class ProfessorScoreSnapshot(BaseModel):
    professor_id: str
    global_score: float | None
    total_evaluations: int


class EvaluationRead(BaseModel):
    """Respuesta de POST /evaluations."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    professor_id: str
    course_id: int
    semester: str
    clarity: int
    easiness: int
    helpfulness: int
    punctuality: int
    modality: str
    created_at: datetime

    comment: CommentEmbedded | None = None
    professor_score: ProfessorScoreSnapshot | None = None
    hashtags: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Comment (lectura publica — anonimo, sin user_id)
# ---------------------------------------------------------------------------

class CommentRead(BaseModel):
    """Shape publico de Comment. Solo items status='published'. SIN user_id (RF-18)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    professor_id: str
    course_id: int
    text: str | None
    modality: str
    like_count: int
    dislike_count: int
    created_at: datetime
    hashtags: list[str] = Field(default_factory=list)
    author: Literal["Anónimo"] = "Anónimo"


# ---------------------------------------------------------------------------
# Reactions / Reports
# ---------------------------------------------------------------------------

ReactionType = Literal["like", "dislike"]
ReportReason = Literal["spam", "hate_speech", "harassment", "off_topic", "other"]


class ReactionCreate(BaseModel):
    type: ReactionType


class ReactionResult(BaseModel):
    """Resultado del toggle: el estado FINAL del registro tras la operacion."""

    comment_id: str
    user_reaction: ReactionType | None  # None si fue toggle-off
    like_count: int
    dislike_count: int


class ReportCreate(BaseModel):
    reason: ReportReason
    description: str | None = Field(default=None, max_length=500)


class ReportResult(BaseModel):
    comment_id: str
    reports_count: int


# ---------------------------------------------------------------------------
# Hashtags
# ---------------------------------------------------------------------------

class HashtagSuggestion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    label: str
    usage_count: int


__all__ = [
    "CommentEmbedded",
    "CommentRead",
    "CourseCreate",
    "CourseRead",
    "EvaluationCreate",
    "EvaluationRead",
    "HashtagSuggestion",
    "Modality",
    "ProfessorScoreSnapshot",
    "ReactionCreate",
    "ReactionResult",
    "ReactionType",
    "ReportCreate",
    "ReportReason",
    "ReportResult",
]
