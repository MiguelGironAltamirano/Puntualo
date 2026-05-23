"""app/modules/evaluations/routers/hashtags.py"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.async_session import get_async_db
from app.modules.evaluations.schemas import HashtagSuggestion
from app.modules.evaluations.service.hashtag_service import HashtagService

router = APIRouter()


@router.get(
    "/hashtags",
    response_model=list[HashtagSuggestion],
    summary="Autocompletado de hashtags por prefijo (ordenado por usage_count DESC)",
)
async def autocomplete_hashtags(
    prefix: str = Query("", max_length=50),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_async_db),
):
    svc = HashtagService(db)
    return await svc.autocomplete(prefix=prefix, limit=limit)
