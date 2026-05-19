from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.async_session import get_async_db
from app.models.user import User
from app.modules.auth.dependencies import get_current_user
from app.modules.professors.schemas import (
    ProfessorCreate,
    ProfessorOut,
    ProfessorUpdate,
    RevalidateResponse,
)
from app.modules.professors.service import (
    FacultyNotFoundError,
    InvalidValidationStatusError,
    ProfessorAlreadyExistsError,
    ProfessorService,
    UniversityNotFoundError,
)
from app.schemas.error import ErrorResponse
from app.schemas.pagination import PaginatedResponse
from app.utils.pagination import PaginationParams, paginate

router = APIRouter()


@router.post(
    "/",
    response_model=ProfessorOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo profesor",
    responses={
        404: {"model": ErrorResponse, "description": "Universidad o facultad no encontrada"},
        409: {"model": ErrorResponse, "description": "Profesor duplicado"},
    },
)
async def create_professor(
    payload: ProfessorCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfessorService(db)
    try:
        return await service.create(payload, registered_by_id=current_user.id)
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


@router.get(
    "/",
    response_model=PaginatedResponse[ProfessorOut],
    summary="Listar profesores (paginado)",
)
async def list_professors(
    pagination: PaginationParams = Depends(),
    search: str | None = Query(None, max_length=200),
    db: AsyncSession = Depends(get_async_db),
):
    service = ProfessorService(db)
    query = service.list_query(search=search)
    return await paginate(db, query, pagination, ProfessorOut)


@router.get(
    "/{professor_id}",
    response_model=ProfessorOut,
    summary="Obtener profesor por id",
    responses={
        404: {"model": ErrorResponse, "description": "Profesor no encontrado"},
    },
)
async def get_professor(
    professor_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    service = ProfessorService(db)
    professor = await service.get_by_id(professor_id)
    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFESSOR_NOT_FOUND", "message": "Profesor no encontrado"},
        )
    return professor


@router.patch(
    "/{professor_id}",
    response_model=ProfessorOut,
    summary="Actualizar profesor",
    responses={
        404: {"model": ErrorResponse, "description": "Profesor no encontrado"},
        409: {"model": ErrorResponse, "description": "Profesor duplicado"},
    },
)
async def update_professor(
    professor_id: str,
    payload: ProfessorUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfessorService(db)
    try:
        professor = await service.update(professor_id, payload)
    except ProfessorAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "PROFESSOR_DUPLICATE", "message": str(exc)},
        )
    except InvalidValidationStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "INVALID_VALIDATION_STATUS", "message": str(exc)},
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
    return professor


@router.post(
    "/{professor_id}/revalidate",
    response_model=RevalidateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Forzar revalidación del profesor",
    responses={
        404: {"model": ErrorResponse, "description": "Profesor no encontrado"},
    },
)
async def revalidate_professor(
    professor_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfessorService(db)
    queued = await service.revalidate(professor_id)
    if not queued:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFESSOR_NOT_FOUND", "message": "Profesor no encontrado"},
        )
    return RevalidateResponse(queued=True, professor_id=professor_id)


@router.delete(
    "/{professor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar profesor (soft delete)",
    responses={
        404: {"model": ErrorResponse, "description": "Profesor no encontrado"},
    },
)
async def delete_professor(
    professor_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfessorService(db)
    deleted = await service.soft_delete(professor_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFESSOR_NOT_FOUND", "message": "Profesor no encontrado"},
        )
    return None
