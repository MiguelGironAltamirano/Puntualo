from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.async_session import get_async_db
from app.models.user import User
from app.modules.auth.dependencies import get_current_user
from app.modules.professors.dependencies import (
    is_admin,
    require_admin,
    require_verified_user,
)
from app.modules.professors.router_comparison import router as comparison_router
from app.modules.professors.schemas import (
    VALIDATION_STATUSES,
    AiSummaryOut,
    CourseRef,
    EvidenceRef,
    ProfessorAdminOut,
    ProfessorCourseAdd,
    ProfessorCreate,
    ProfessorDetail,
    ProfessorDetailAdmin,
    ProfessorOut,
    ProfessorUpdate,
    RejectResponse,
    RevalidateResponse,
    SortField,
    SortOrder,
)
from app.modules.professors.service import (
    CourseNotFoundError,
    CoursesNotFoundError,
    FacultyNotFoundError,
    InvalidCourseFacultyError,
    InvalidStateTransitionError,
    ProfessorAlreadyExistsError,
    ProfessorService,
    UniversityNotFoundError,
)
from app.schemas.error import ErrorResponse
from app.schemas.pagination import PaginatedResponse
from app.tasks.nlp_tasks import generate_professor_summary

router = APIRouter()

MAX_PAGE_SIZE = 50


# ---------- create ----------


# Se registra SIN barra final como ruta canónica (el frontend llama a /professors),
# y CON barra como alias oculto. Así se evita el 307 redirect de FastAPI, que detrás
# del proxy HTTPS rompía intermitentemente el CORS con credenciales en el navegador.
@router.post(
    "",
    response_model=ProfessorOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo profesor (usuario verificado)",
    responses={
        403: {"model": ErrorResponse, "description": "Usuario no verificado"},
        404: {"model": ErrorResponse, "description": "Universidad, facultad o curso no encontrado"},
        409: {"model": ErrorResponse, "description": "Profesor duplicado"},
        422: {"model": ErrorResponse, "description": "Curso fuera de la facultad"},
    },
)
@router.post("/", include_in_schema=False)
async def create_professor(
    payload: ProfessorCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_verified_user),
):
    service = ProfessorService(db)
    try:
        professor = await service.create(payload, registered_by_id=current_user.id)
    except ProfessorAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "PROFESSOR_DUPLICATE", "message": str(exc)},
        )
    except UniversityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "UNIVERSITY_NOT_FOUND", "message": str(exc)},
        )
    except FacultyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "FACULTY_NOT_FOUND", "message": str(exc)},
        )
    except CoursesNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "COURSES_NOT_FOUND", "message": str(exc), "ids": exc.ids},
        )
    except InvalidCourseFacultyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "COURSE_WRONG_FACULTY", "message": str(exc)},
        )
    return ProfessorOut.model_validate(professor)


# ---------- list ----------


# Canónica sin barra (evita el 307 redirect que rompía el CORS); alias con barra oculto.
@router.get(
    "",
    response_model=PaginatedResponse[ProfessorOut] | PaginatedResponse[ProfessorAdminOut],
    summary="Listar profesores (paginado, filtros, sort, búsqueda avanzada)",
)
@router.get(
    "/",
    response_model=PaginatedResponse[ProfessorOut] | PaginatedResponse[ProfessorAdminOut],
    include_in_schema=False,
)
async def list_professors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=MAX_PAGE_SIZE),
    search: str | None = Query(None, max_length=200, description="Búsqueda fuzzy en nombre, universidad, facultad"),
    university_id: int | None = Query(None, gt=0),
    faculty_id: int | None = Query(None, gt=0),
    course_id: int | None = Query(None, gt=0),
    validation_status: str | None = Query(None),
    include_deleted: bool = Query(False),
    sort_by: SortField = Query("created_at"),
    sort_order: SortOrder = Query("desc"),
    min_clarity: float | None = Query(None, ge=1.0, le=5.0, description="Calificación mínima de claridad"),
    max_clarity: float | None = Query(None, ge=1.0, le=5.0, description="Calificación máxima de claridad"),
    min_easiness: float | None = Query(None, ge=1.0, le=5.0, description="Dificultad mínima"),
    max_easiness: float | None = Query(None, ge=1.0, le=5.0, description="Dificultad máxima"),
    min_helpfulness: float | None = Query(None, ge=1.0, le=5.0, description="Ayuda mínima"),
    max_helpfulness: float | None = Query(None, ge=1.0, le=5.0, description="Ayuda máxima"),
    min_punctuality: float | None = Query(None, ge=1.0, le=5.0, description="Puntualidad mínima"),
    max_punctuality: float | None = Query(None, ge=1.0, le=5.0, description="Puntualidad máxima"),
    min_global_score: float | None = Query(None, ge=1.0, le=5.0, description="Puntaje global mínimo"),
    max_global_score: float | None = Query(None, ge=1.0, le=5.0, description="Puntaje global máximo"),
    min_evaluations: int | None = Query(None, ge=1, description="Número mínimo de evaluaciones"),
    date_from: str | None = Query(None, description="Fecha de creación desde (ISO format)"),
    date_to: str | None = Query(None, description="Fecha de creación hasta (ISO format)"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    admin = is_admin(current_user)

    if validation_status is not None:
        if validation_status not in VALIDATION_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "INVALID_VALIDATION_STATUS",
                    "message": f"validation_status debe ser uno de {sorted(VALIDATION_STATUSES)}",
                },
            )
        if not admin:
            # No-admin no puede filtrar por estado
            validation_status = None

    if include_deleted and not admin:
        include_deleted = False

    service = ProfessorService(db)
    query = service.list_query(
        search=search,
        university_id=university_id,
        faculty_id=faculty_id,
        course_id=course_id,
        validation_status=validation_status,
        include_deleted=include_deleted,
        hide_rejected=not admin,
        sort_by=sort_by,
        sort_order=sort_order,
        min_clarity=min_clarity,
        max_clarity=max_clarity,
        min_easiness=min_easiness,
        max_easiness=max_easiness,
        min_helpfulness=min_helpfulness,
        max_helpfulness=max_helpfulness,
        min_punctuality=min_punctuality,
        max_punctuality=max_punctuality,
        min_global_score=min_global_score,
        max_global_score=max_global_score,
        min_evaluations=min_evaluations,
        date_from=date_from,
        date_to=date_to,
    )

    count_stmt = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    paginated = query.offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(paginated)).scalars().all())
    total_pages = ceil(total / page_size) if total > 0 else 0

    schema = ProfessorAdminOut if admin else ProfessorOut
    return {
        "items": [schema.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


# ---------- detail ----------


@router.get(
    "/{professor_id}",
    response_model=ProfessorDetail | ProfessorDetailAdmin,
    summary="Obtener detalle enriquecido del profesor",
    responses={
        404: {"model": ErrorResponse, "description": "Profesor no encontrado"},
    },
)
async def get_professor(
    professor_id: str,
    include_deleted: bool = Query(False),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    admin = is_admin(current_user)
    if include_deleted and not admin:
        include_deleted = False

    service = ProfessorService(db)
    detail = await service.get_detail(professor_id, include_deleted=include_deleted)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFESSOR_NOT_FOUND", "message": "Profesor no encontrado"},
        )

    (professor, courses, degrees, evidence, summary,
     university_name, faculty_name, ai_summary_row, ai_summary_reason) = detail

    # Ocultar profesores rejected a no-admin
    if not admin and professor.validation_status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFESSOR_NOT_FOUND", "message": "Profesor no encontrado"},
        )

    base_data = {
        "id": str(professor.id),
        "full_name": professor.full_name,
        "university_id": professor.university_id,
        "faculty_id": professor.faculty_id,
        "university_name": university_name,
        "faculty_name": faculty_name,
        "validation_status": professor.validation_status,
        "global_score": float(professor.global_score) if professor.global_score is not None else None,
        "total_evaluations": professor.total_evaluations,
        "is_active": professor.is_active,
        "created_at": professor.created_at,
        "updated_at": professor.updated_at,
        "courses": [CourseRef.model_validate(c) for c in courses],
        "degrees": degrees,
        "evidence": [EvidenceRef.model_validate(e) for e in evidence],
        "executive_summary": summary,
        "ai_summary": AiSummaryOut.model_validate(ai_summary_row) if ai_summary_row else None,
        "ai_summary_reason": ai_summary_reason,
    }

    if admin:
        return ProfessorDetailAdmin(
            **base_data,
            registered_by_id=str(professor.registered_by_id) if professor.registered_by_id else None,
            deleted_at=professor.deleted_at,
        )
    return ProfessorDetail(**base_data)


# ---------- update / delete (admin) ----------


@router.patch(
    "/{professor_id}",
    response_model=ProfessorAdminOut,
    summary="Actualizar profesor (admin)",
    responses={
        403: {"model": ErrorResponse, "description": "Acceso denegado"},
        404: {"model": ErrorResponse, "description": "Profesor / Universidad / Facultad no encontrada"},
        409: {"model": ErrorResponse, "description": "Profesor duplicado"},
    },
)
async def update_professor(
    professor_id: str,
    payload: ProfessorUpdate,
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(require_admin),
):
    service = ProfessorService(db)
    try:
        professor = await service.update(professor_id, payload)
    except ProfessorAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "PROFESSOR_DUPLICATE", "message": str(exc)},
        )
    except UniversityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "UNIVERSITY_NOT_FOUND", "message": str(exc)},
        )
    except FacultyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "FACULTY_NOT_FOUND", "message": str(exc)},
        )

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFESSOR_NOT_FOUND", "message": "Profesor no encontrado"},
        )
    return ProfessorAdminOut.model_validate(professor)


@router.delete(
    "/{professor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete profesor (admin)",
    responses={
        403: {"model": ErrorResponse, "description": "Acceso denegado"},
        404: {"model": ErrorResponse, "description": "Profesor no encontrado"},
    },
)
async def delete_professor(
    professor_id: str,
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(require_admin),
):
    service = ProfessorService(db)
    deleted = await service.soft_delete(professor_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFESSOR_NOT_FOUND", "message": "Profesor no encontrado"},
        )
    return None


# ---------- estado: revalidate / reject (admin) ----------


@router.post(
    "/{professor_id}/revalidate",
    response_model=RevalidateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Forzar revalidación del pipeline (admin)",
    responses={
        403: {"model": ErrorResponse, "description": "Acceso denegado"},
        404: {"model": ErrorResponse, "description": "Profesor no encontrado"},
    },
)
async def revalidate_professor(
    professor_id: str,
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(require_admin),
):
    service = ProfessorService(db)
    queued = await service.revalidate(professor_id)
    if not queued and (await service.get_by_id(professor_id, include_inactive=True)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFESSOR_NOT_FOUND", "message": "Profesor no encontrado"},
        )
    return RevalidateResponse(queued=queued, professor_id=professor_id)


@router.post(
    "/{professor_id}/reject",
    response_model=RejectResponse,
    summary="Rechazar profesor not_found (admin)",
    responses={
        403: {"model": ErrorResponse, "description": "Acceso denegado"},
        404: {"model": ErrorResponse, "description": "Profesor no encontrado"},
        422: {"model": ErrorResponse, "description": "Transición de estado inválida"},
    },
)
async def reject_professor(
    professor_id: str,
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(require_admin),
):
    service = ProfessorService(db)
    try:
        professor = await service.reject(professor_id)
    except InvalidStateTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "INVALID_STATE_TRANSITION",
                "message": str(exc),
                "current_status": exc.current_status,
            },
        )
    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFESSOR_NOT_FOUND", "message": "Profesor no encontrado"},
        )
    return RejectResponse(
        professor_id=str(professor.id),
        validation_status=professor.validation_status,
    )


@router.post(
    "/{professor_id}/regenerate-summary",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Regenerar resumen IA del profesor (admin)",
    responses={
        403: {"model": ErrorResponse, "description": "Acceso denegado"},
        404: {"model": ErrorResponse, "description": "Profesor no encontrado"},
    },
)
async def regenerate_summary(
    professor_id: str,
    db: AsyncSession = Depends(get_async_db),
    _admin: User = Depends(require_admin),
):
    service = ProfessorService(db)
    professor = await service.get_by_id(professor_id, include_inactive=True)
    if professor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFESSOR_NOT_FOUND", "message": "Profesor no encontrado"},
        )
    queued = True
    try:
        generate_professor_summary.delay(str(professor_id), True)
    except Exception:  # broker caído: no rompemos la respuesta admin
        queued = False
    return {"queued": queued, "professor_id": str(professor_id)}


# ---------- gestión de cursos ----------


@router.get(
    "/{professor_id}/courses",
    response_model=list[CourseRef],
    summary="Listar cursos que dicta el profesor",
    responses={
        404: {"model": ErrorResponse, "description": "Profesor no encontrado"},
    },
)
async def list_professor_courses(
    professor_id: str,
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(get_current_user),
):
    service = ProfessorService(db)
    professor = await service.get_by_id(professor_id)
    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFESSOR_NOT_FOUND", "message": "Profesor no encontrado"},
        )
    courses = await service.list_courses(professor_id)
    return [CourseRef.model_validate(c) for c in courses]


@router.post(
    "/{professor_id}/courses",
    status_code=status.HTTP_201_CREATED,
    summary="Asignar curso al profesor (admin)",
    responses={
        403: {"model": ErrorResponse, "description": "Acceso denegado"},
        404: {"model": ErrorResponse, "description": "Profesor o curso no encontrado"},
        422: {"model": ErrorResponse, "description": "Curso no pertenece a la facultad del profesor"},
    },
)
async def add_professor_course(
    professor_id: str,
    payload: ProfessorCourseAdd,
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(require_admin),
):
    service = ProfessorService(db)
    try:
        ok = await service.add_course(professor_id, payload.course_id)
    except CourseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "COURSE_NOT_FOUND", "message": str(exc)},
        )
    except InvalidCourseFacultyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "INVALID_COURSE_FACULTY", "message": str(exc)},
        )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFESSOR_NOT_FOUND", "message": "Profesor no encontrado"},
        )
    return {"professor_id": professor_id, "course_id": payload.course_id}


@router.delete(
    "/{professor_id}/courses/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desasignar curso del profesor (admin)",
    responses={
        403: {"model": ErrorResponse, "description": "Acceso denegado"},
        404: {"model": ErrorResponse, "description": "Relación no encontrada"},
    },
)
async def remove_professor_course(
    professor_id: str,
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(require_admin),
):
    service = ProfessorService(db)
    removed = await service.remove_course(professor_id, course_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFESSOR_COURSE_NOT_FOUND", "message": "Relación profesor-curso no encontrada"},
        )
    return None


# Include comparison router
router.include_router(comparison_router)
