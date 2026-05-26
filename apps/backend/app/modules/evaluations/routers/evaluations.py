"""app/modules/evaluations/routers/evaluations.py

Endpoints:
   POST /evaluations          — crear evaluacion (verified user)
   GET  /evaluations/mine     — listar mis evaluaciones (autenticado)
   GET  /evaluations          — listar todas las evaluaciones (público, filtrable, paginado)
"""
from __future__ import annotations

from math import ceil

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.async_session import get_async_db
from app.models.evaluation import Evaluation
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
from app.schemas.pagination import PaginatedResponse

router = APIRouter()

MAX_PAGE_SIZE = 50


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


@router.get(
    "/evaluations",
    summary="Listar todas las evaluaciones (público, filtrable, paginado)",
)
async def list_evaluations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=MAX_PAGE_SIZE),
    professor_id: str | None = Query(None, description="Filtrar por profesor"),
    course_id: int | None = Query(None, gt=0, description="Filtrar por curso"),
    semester: str | None = Query(None, max_length=7, description="Filtrar por semestre (ej: 2024-1)"),
    modality: str | None = Query(None, regex="^(virtual|presencial|ambas)$", description="Filtrar por modalidad"),
    min_clarity: int | None = Query(None, ge=1, le=5),
    max_clarity: int | None = Query(None, ge=1, le=5),
    min_easiness: int | None = Query(None, ge=1, le=5),
    max_easiness: int | None = Query(None, ge=1, le=5),
    min_helpfulness: int | None = Query(None, ge=1, le=5),
    max_helpfulness: int | None = Query(None, ge=1, le=5),
    min_punctuality: int | None = Query(None, ge=1, le=5),
    max_punctuality: int | None = Query(None, ge=1, le=5),
    date_from: str | None = Query(None, description="Fecha desde (ISO format)"),
    date_to: str | None = Query(None, description="Fecha hasta (ISO format)"),
    sort_by: str = Query("created_at", regex="^(created_at|clarity|easiness|helpfulness|punctuality)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    List all evaluations with advanced filtering and pagination.
    
    Public endpoint - no authentication required.
    """
    # Build base query
    base_query = select(Evaluation)
    
    # Apply filters
    filters = []
    
    if professor_id:
        filters.append(Evaluation.professor_id == professor_id)
    
    if course_id is not None:
        filters.append(Evaluation.course_id == course_id)
    
    if semester:
        filters.append(Evaluation.semester == semester)
    
    if modality:
        filters.append(Evaluation.modality == modality)
    
    if min_clarity is not None:
        filters.append(Evaluation.clarity >= min_clarity)
    if max_clarity is not None:
        filters.append(Evaluation.clarity <= max_clarity)
    
    if min_easiness is not None:
        filters.append(Evaluation.easiness >= min_easiness)
    if max_easiness is not None:
        filters.append(Evaluation.easiness <= max_easiness)
    
    if min_helpfulness is not None:
        filters.append(Evaluation.helpfulness >= min_helpfulness)
    if max_helpfulness is not None:
        filters.append(Evaluation.helpfulness <= max_helpfulness)
    
    if min_punctuality is not None:
        filters.append(Evaluation.punctuality >= min_punctuality)
    if max_punctuality is not None:
        filters.append(Evaluation.punctuality <= max_punctuality)
    
    # Date range filters
    from datetime import datetime
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from)
            filters.append(Evaluation.created_at >= from_date)
        except (ValueError, TypeError):
            pass
    
    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to)
            filters.append(Evaluation.created_at <= to_date)
        except (ValueError, TypeError):
            pass
    
    if filters:
        base_query = base_query.where(and_(*filters))
    
    # Count total
    count_stmt = select(func.count()).select_from(Evaluation)
    if filters:
        count_stmt = count_stmt.where(and_(*filters))
    total = (await db.execute(count_stmt)).scalar_one()
    
    # Apply sorting
    sort_column_map = {
        "created_at": Evaluation.created_at,
        "clarity": Evaluation.clarity,
        "easiness": Evaluation.easiness,
        "helpfulness": Evaluation.helpfulness,
        "punctuality": Evaluation.punctuality,
    }
    sort_column = sort_column_map[sort_by]
    order = sort_column.desc() if sort_order == "desc" else sort_column.asc()
    base_query = base_query.order_by(order, Evaluation.id.desc())
    
    # Apply pagination
    paginated = base_query.offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(paginated)).scalars().all())
    
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    return {
        "items": [
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
            for e in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }
