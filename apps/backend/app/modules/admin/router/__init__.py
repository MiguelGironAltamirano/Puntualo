"""Admin router module."""
from fastapi import APIRouter

from app.modules.admin.router.admin_router import router as _moderation_router
from app.modules.admin.router.professor_validation import router as _validation_router

router = APIRouter()
router.include_router(_moderation_router)
router.include_router(_validation_router)

__all__ = ["router"]
