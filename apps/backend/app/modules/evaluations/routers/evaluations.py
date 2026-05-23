"""app/modules/evaluations/routers/evaluations.py

Endpoints:
  POST /evaluations          — crear evaluacion (verified user)
  GET  /evaluations/mine     — listar mis evaluaciones (autenticado)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.async_session import get_async_db
from app.models.user import User
from app.modules.auth.dependencies import get_current_user
from app.modules.evaluations.schemas import (
    CommentEmbedded,
    EvaluationCreate,
    EvaluationRead,
    ProfessorScoreSnapshot,
)
from app.modules.evaluations.service.evaluation_service import EvaluationService
from app.modules.professors.dependencies import require_verified_user
from app.schemas.error import ErrorResponse

router = APIRouter()


@router.post(
    "/evaluations",
    response_model=EvaluationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear evaluacion multi-criterio (con comentario y hashtags opcionales)",
    responses={
        403: {"model": ErrorResponse, "description": "Usuario no verificado o profesor no validado"},
        404: {"model": ErrorResponse, "description": "Profesor o curso no encontrado"},
        409: {"model": ErrorResponse, "description": "Evaluacion duplicada"},
        422: {"model": ErrorResponse, "description": "Validacion fallida (hashtags, banned terms, curso no dictado)"},
    },
)
async def create_evaluation(
    payload: EvaluationCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_verified_user),
) -> EvaluationRead:
    svc = EvaluationService(db)
    result = await svc.create(current_user, payload)

    embedded: CommentEmbedded | None = None
    if result.comment is not None:
        embedded = CommentEmbedded(
            id=str(result.comment.id),
            text=result.comment.text,
            modality=result.comment.modality,
            status=result.comment.status,
            like_count=result.comment.like_count,
            dislike_count=result.comment.dislike_count,
            created_at=result.comment.created_at,
        )

    snapshot = ProfessorScoreSnapshot(
        professor_id=str(result.professor.id),
        global_score=float(result.professor.global_score) if result.professor.global_score is not None else None,
        total_evaluations=result.professor.total_evaluations,
    )

    return EvaluationRead(
        id=str(result.evaluation.id),
        user_id=str(result.evaluation.user_id),
        professor_id=str(result.evaluation.professor_id),
        course_id=result.evaluation.course_id,
        semester=result.evaluation.semester,
        clarity=result.evaluation.clarity,
        easiness=result.evaluation.easiness,
        helpfulness=result.evaluation.helpfulness,
        punctuality=result.evaluation.punctuality,
        modality=result.evaluation.modality,
        created_at=result.evaluation.created_at,
        comment=embedded,
        professor_score=snapshot,
        hashtags=result.hashtags,
    )


@router.get(
    "/evaluations/mine",
    summary="Listar mis evaluaciones (filtrable por profesor/curso/semestre)",
)
async def list_my_evaluations(
    professor_id: str | None = Query(default=None),
    course_id: int | None = Query(default=None),
    semester: str | None = Query(default=None),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    svc = EvaluationService(db)
    evals = await svc.get_my_evaluations(
        current_user,
        professor_id=professor_id,
        course_id=course_id,
        semester=semester,
    )
    return [
        {
            "id": str(e.id),
            "professor_id": str(e.professor_id),
            "course_id": e.course_id,
            "semester": e.semester,
            "clarity": e.clarity,
            "easiness": e.easiness,
            "helpfulness": e.helpfulness,
            "punctuality": e.punctuality,
            "modality": e.modality,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in evals
    ]
