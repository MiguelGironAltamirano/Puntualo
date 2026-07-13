"""Courses endpoint - List active courses with pagination and filters."""
from math import ceil

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.async_session import get_async_db
from app.models.course import Course
from app.models.evaluation import Evaluation
from app.modules.evaluations.schemas import CourseRead
from app.modules.evaluations.service.course_service import CourseService
from app.schemas.pagination import PaginatedResponse

router = APIRouter()

MAX_PAGE_SIZE = 50


@router.get(
    "/courses",
    response_model=PaginatedResponse[CourseRead],
    summary="Listar cursos activos (paginado, filtros, fuzzy search)",
)
async def list_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=MAX_PAGE_SIZE),
    q: str | None = Query(None, max_length=200, description="Fuzzy search on course name"),
    university_id: int | None = Query(None, gt=0),
    faculty_id: int | None = Query(None, gt=0),
    sort_by: str = Query("name", pattern="^(name|evaluation_count)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    List active courses with advanced filtering and pagination.

    Query Parameters:
    - q: Fuzzy search on course name (case-insensitive LIKE)
    - university_id: Filter by university
    - faculty_id: Filter by faculty
    - sort_by: Sort by 'name' or 'evaluation_count'
    - sort_order: 'asc' or 'desc'
    - page: Page number (1-indexed)
    - page_size: Items per page (1-50)
    """
    service = CourseService(db)

    # Get base query with filters. list_query() applies its own default
    # ordering (created_at desc) for other callers (chatbot tool) — clear it
    # here since this endpoint has its own sort_by/sort_order contract.
    base_query = service.list_query(q=q, university_id=university_id).order_by(None)

    # Apply faculty filter if provided
    if faculty_id is not None:
        base_query = base_query.where(Course.faculty_id == faculty_id)
    
    # Handle sorting
    if sort_by == "evaluation_count":
        # Left join with evaluations to count them
        eval_count_subquery = (
            select(Evaluation.course_id, func.count(Evaluation.id).label("eval_count"))
            .group_by(Evaluation.course_id)
            .subquery()
        )
        base_query = base_query.outerjoin(
            eval_count_subquery, Course.id == eval_count_subquery.c.course_id
        ).add_columns(func.coalesce(eval_count_subquery.c.eval_count, 0).label("eval_count"))
        
        # Apply sorting by evaluation count
        if sort_order == "desc":
            base_query = base_query.order_by(func.coalesce(eval_count_subquery.c.eval_count, 0).desc())
        else:
            base_query = base_query.order_by(func.coalesce(eval_count_subquery.c.eval_count, 0).asc())
        base_query = base_query.order_by(Course.name.asc())  # Secondary sort
    else:
        # Sort by name (default)
        order_col = Course.name.desc() if sort_order == "desc" else Course.name.asc()
        base_query = base_query.order_by(order_col)
    
    # Count total items
    count_stmt = select(func.count()).select_from(Course).where(Course.is_active.is_(True))
    if q:
        term = f"%{q.strip().lower()}%"
        count_stmt = count_stmt.where(func.lower(Course.name).like(term))
    if university_id is not None:
        count_stmt = count_stmt.where(Course.university_id == university_id)
    if faculty_id is not None:
        count_stmt = count_stmt.where(Course.faculty_id == faculty_id)
    
    total = (await db.execute(count_stmt)).scalar_one()
    
    # Apply pagination
    paginated = base_query.offset((page - 1) * page_size).limit(page_size)
    results = (await db.execute(paginated)).all()
    
    # Extract courses and evaluation counts
    courses_with_counts = []
    for row in results:
        if sort_by == "evaluation_count":
            course = row[0]
            eval_count = row[1]
        else:
            course = row[0]
            eval_count = 0
        courses_with_counts.append((course, eval_count))
    
    # If we need actual evaluation counts and we only have defaults, fetch them
    if sort_by != "evaluation_count" and courses_with_counts:
        course_ids = [c[0].id for c in courses_with_counts]
        eval_count_stmt = (
            select(Evaluation.course_id, func.count(Evaluation.id).label("count"))
            .where(Evaluation.course_id.in_(course_ids))
            .group_by(Evaluation.course_id)
        )
        eval_counts_result = await db.execute(eval_count_stmt)
        eval_counts_map = {row[0]: row[1] for row in eval_counts_result.all()}
        courses_with_counts = [(c, eval_counts_map.get(c.id, 0)) for c, _ in courses_with_counts]
    
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    return {
        "items": [
            CourseRead(
                id=c.id,
                name=c.name,
                faculty_id=c.faculty_id,
                university_id=c.university_id,
                evaluation_count=eval_count,
                created_at=c.created_at,
            )
            for c, eval_count in courses_with_counts
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }
