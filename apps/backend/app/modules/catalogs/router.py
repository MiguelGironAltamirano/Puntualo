from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.async_session import get_async_db
from app.modules.catalogs.schemas import FacultyOut, UniversityOut
from app.modules.catalogs.service import CatalogService
from app.schemas.error import ErrorResponse

router = APIRouter()


@router.get(
    "/universities",
    response_model=list[UniversityOut],
    summary="Listar universidades disponibles",
)
async def list_universities(
    db: AsyncSession = Depends(get_async_db),
):
    service = CatalogService(db)
    universities = await service.list_universities()
    return [UniversityOut.model_validate(u) for u in universities]


@router.get(
    "/universities/{university_id}/faculties",
    response_model=list[FacultyOut],
    summary="Listar facultades de una universidad",
    responses={
        404: {"model": ErrorResponse, "description": "Universidad no encontrada"},
    },
)
async def list_faculties(
    university_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    service = CatalogService(db)
    university = await service.get_university(university_id)
    if university is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "UNIVERSITY_NOT_FOUND",
                "message": f"Universidad id={university_id} no encontrada",
            },
        )

    faculties = await service.list_faculties(university_id)
    return [FacultyOut.model_validate(f) for f in faculties]
