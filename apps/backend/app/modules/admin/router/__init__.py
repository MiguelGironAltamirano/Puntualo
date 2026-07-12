"""Admin router module."""
from fastapi import APIRouter

from app.modules.admin.router.professor_validation import router as _validation_router

router = APIRouter()
router.include_router(_validation_router)

__all__ = ["router"]
