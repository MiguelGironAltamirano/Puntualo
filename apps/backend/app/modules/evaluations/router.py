"""Router raiz del modulo evaluations: monta todos los sub-routers."""
from fastapi import APIRouter

from app.modules.evaluations.routers.comments import router as comments_subrouter
from app.modules.evaluations.routers.courses import router as courses_subrouter
from app.modules.evaluations.routers.evaluations import router as evaluations_subrouter
from app.modules.evaluations.routers.hashtags import router as hashtags_subrouter
from app.modules.evaluations.routers.reactions import router as reactions_subrouter
from app.modules.evaluations.routers.reports import router as reports_subrouter

router = APIRouter()
router.include_router(courses_subrouter)
router.include_router(evaluations_subrouter)
router.include_router(comments_subrouter)
router.include_router(reactions_subrouter)
router.include_router(reports_subrouter)
router.include_router(hashtags_subrouter)
