from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Puntualo backend funcionando"}


@app.get("/health/db")
def check_db():

    with engine.connect() as connection:

        connection.execute(text("SELECT 1"))

    return {"database": "connected"}