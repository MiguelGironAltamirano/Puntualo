from fastapi import FastAPI
from sqlalchemy import text

import app.core.celery_app  # noqa: F401 — ensures shared_task binds to Redis broker
from app.db.session import engine
from app.modules.auth.router import router as auth_router
from app.modules.professors.router import router as professors_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

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