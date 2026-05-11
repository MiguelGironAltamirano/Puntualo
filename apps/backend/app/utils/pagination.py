from math import ceil
from typing import TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.pagination import PaginatedResponse

T = TypeVar("T", bound=BaseModel)


class PaginationParams:
    """Dependencia inyectable para paginación estándar."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Número de página"),
        page_size: int = Query(20, ge=1, le=100, description="Resultados por página"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


async def paginate(
    db: AsyncSession,
    query,
    params: PaginationParams,
    schema: type[T],
) -> dict:
    """Ejecuta una query con paginación y retorna el formato estándar de PaginatedResponse."""
    count_stmt = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    paginated_query = query.offset(params.offset).limit(params.page_size)
    result = await db.execute(paginated_query)
    items = result.scalars().all()

    total_pages = ceil(total / params.page_size) if total > 0 else 0

    return {
        "items": [schema.model_validate(item) for item in items],
        "total": total,
        "page": params.page,
        "page_size": params.page_size,
        "total_pages": total_pages,
        "has_next": params.page < total_pages,
        "has_prev": params.page > 1,
    }
