import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

import app.core.celery_app  # noqa: F401 — ensures shared_task binds to Redis broker
from app.db.session import engine
from app.modules.auth.router import router as auth_router
from app.modules.catalogs.router import router as catalogs_router
from app.modules.evaluations.errors import DomainError
from app.modules.evaluations.router import router as evaluations_router
from app.modules.professors.router import router as professors_router
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

app = FastAPI()


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Traduce DomainError -> ErrorResponse { detail: { code, message } }."""
    logger.warning(
        "domain_error | code=%s | status=%s | path=%s | message=%s",
        exc.code,
        exc.status_code,
        request.url.path,
        exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": {"code": exc.code, "message": exc.message}},
    )

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # en dev, la URL del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Puntualo backend funcionando"}


@app.get("/health/db")
def check_db():

    with engine.connect() as connection:

        connection.execute(text("SELECT 1"))

    return {"database": "connected"}

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    professors_router,
    prefix="/professors",
    tags=["professors"],
)

app.include_router(
    evaluations_router,
    tags=["evaluations"],
)

app.include_router(
    catalogs_router,
    tags=["catalogs"],
)