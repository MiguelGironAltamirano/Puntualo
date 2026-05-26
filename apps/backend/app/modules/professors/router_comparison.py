"""Professor comparison endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.async_session import get_async_db
from app.modules.professors.service_comparison import ComparisonService

router = APIRouter()

MAX_PROFESSORS = 4


class CompareRequest(BaseModel):
    """Request payload for comparison."""
    professor_ids: list[str] = None  # IDs of professors to compare

    class Config:
        json_schema_extra = {
            "example": {
                "professor_ids": ["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"]
            }
        }


@router.post(
    "/compare",
    summary="Comparar 2-4 profesores lado a lado",
    description="Compara múltiples profesores y devuelve datos agregados para análisis."
)
async def compare_professors(
    request: CompareRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Compare 2-4 professors side-by-side.
    
    Returns aggregated data including:
    - Basic profile info (name, university, faculty)
    - Average scores for all metrics
    - Evaluation breakdown by modality
    - Common courses taught
    - Recent comments
    - AI summaries
    - Comparison metrics (best in each category)
    """
    
    # Validate input
    if not request.professor_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "MISSING_IDS", "message": "profesor_ids is required"},
        )
    
    professor_ids = list(set(request.professor_ids))  # Remove duplicates
    
    if len(professor_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "TOO_FEW_PROFESSORS", "message": "At least 2 professors required for comparison"},
        )
    
    if len(professor_ids) > MAX_PROFESSORS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "TOO_MANY_PROFESSORS",
                "message": f"Maximum {MAX_PROFESSORS} professors allowed for comparison",
            },
        )
    
    # Validate IDs format
    try:
        from uuid import UUID
        for pid in professor_ids:
            UUID(pid)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_ID_FORMAT", "message": "Invalid professor ID format"},
        )
    
    # Get comparison data
    service = ComparisonService(db)
    result = await service.get_comparison_data(professor_ids)
    
    if not result["professors"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFESSORS_NOT_FOUND", "message": "One or more professors not found"},
        )
    
    return result


@router.get(
    "/compare",
    summary="Comparar profesores (query string version)",
    description="Alternative endpoint using query string IDs",
)
async def compare_professors_get(
    ids: list[str] = Query(..., description="Professor IDs to compare (comma-separated or multiple params)"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Compare professors using query parameters.
    
    Usage:
    - /professors/compare?ids=id1&ids=id2&ids=id3
    """
    request = CompareRequest(professor_ids=ids)
    return await compare_professors(request, db)
