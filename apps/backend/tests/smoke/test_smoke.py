"""
Pruebas de humo — el sistema arranca y responde tras un cambio/despliegue.

Nivel:   Sistema
Tipo:    Asociada al Cambio (Humo)
Técnica: Caja Negra
Objetivo: verificación mínima y rápida de que la app levanta y sus endpoints
          de salud responden. Se corre antes de una suite completa o de un deploy.

Bajo prueba: app/main.py + /health/db
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool


@pytest.fixture
def smoke_client(monkeypatch):
    """TestClient sobre la app real, con el engine de /health/db apuntando a
    SQLite en memoria (evita depender de una BD Postgres real en CI)."""
    import app.main as main

    sqlite_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr(main, "engine", sqlite_engine)

    with TestClient(main.app) as client:
        yield client

    sqlite_engine.dispose()


class TestSmoke:
    def test_app_starts(self, smoke_client):
        """La aplicación se instancia/levanta sin errores y responde en la raíz."""
        resp = smoke_client.get("/")
        assert resp.status_code == 200
        assert resp.json() == {"message": "Puntualo backend funcionando"}

    def test_health_db_responds_200(self, smoke_client):
        """/health/db responde 200 (SELECT 1 a la base)."""
        resp = smoke_client.get("/health/db")
        assert resp.status_code == 200
        assert resp.json() == {"database": "connected"}

    def test_openapi_available(self, smoke_client):
        """El esquema OpenAPI se sirve correctamente e incluye rutas."""
        resp = smoke_client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert schema.get("openapi")
        assert "/auth/login" in schema.get("paths", {})
