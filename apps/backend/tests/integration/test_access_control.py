"""
Pruebas de integración de control de acceso (autorización de endpoints).

Nivel:   Integración
Tipo:    No Funcional (Seguridad)
Técnica: Caja Negra
Objetivo: confirmar que las rutas protegidas exigen token y rol adecuado.

Bajo prueba: dependencias de auth (`get_current_user`, `require_admin`) aplicadas
a los routers protegidos (`/professors`, `/admin`).

Trazabilidad: R3 (acceso no autorizado / IDOR) y OWASP A01 (Broken Access Control).

Nota sobre los códigos "sin token": el esquema de seguridad es `HTTPBearer` con
`auto_error=True`. Cuando falta por completo la cabecera `Authorization`, FastAPI
responde **403** ("Not authenticated"); cuando el token existe pero es inválido,
`get_current_user` responde **401**. Ambos significan "no autenticado", por eso las
aserciones de ausencia de credenciales aceptan {401, 403} (mismo criterio que
`test_auth_api.py::test_me_requires_authentication`).
"""
import uuid

import pytest

from app.core.security import create_access_token
from app.db.async_session import get_async_db
from app.db.session import get_db
from app.main import app
from app.models.user import User

STUDENT_EMAIL = "alumno.acceso@unmsm.edu.pe"


async def _noop_async_db():
    """Override de `get_async_db` que no toca la BD real.

    En las rutas protegidas la dependencia async se resuelve antes que la de auth;
    con este override la resolución no abre conexión a Postgres. El cuerpo del
    endpoint nunca llega a ejecutarse en los casos sin token (auth falla primero).
    """
    yield None


@pytest.fixture
def access_client(sync_db_session):
    """TestClient con `get_db`/`get_async_db` apuntando a la BD de pruebas.

    Siembra además un usuario con rol `student` para poder emitir un token válido
    de rol insuficiente y verificar el 403 en rutas de administrador.
    """
    from fastapi.testclient import TestClient

    # `id` es PGUUID(as_uuid=True) -> requiere un uuid.UUID (no str) al bindear en
    # SQLite. `full_name`/`hashed_password` son NOT NULL. Construimos el usuario
    # completo aquí en vez de reusar las fixtures compartidas (desalineadas con el
    # modelo actual, ver 04_automatizacion_y_cicd.md §4.6).
    student = User(
        id=uuid.uuid4(),
        email=STUDENT_EMAIL,
        full_name="Alumno Acceso",
        username="alumno_acceso",
        hashed_password="not-used-in-this-test",
        is_active=True,
        role="student",
    )
    sync_db_session.add(student)
    sync_db_session.commit()

    def _override_get_db():
        yield sync_db_session

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_async_db] = _noop_async_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_async_db, None)


class TestAccessControl:
    def test_protected_route_without_token_returns_401(self, access_client):
        """`GET /professors` sin token no expone el listado (401/403)."""
        resp = access_client.get("/professors")
        assert resp.status_code in (401, 403), resp.text

    def test_write_endpoint_without_token_returns_401(self, access_client):
        """Un endpoint de escritura (`PATCH /professors/{id}`) sin token es rechazado."""
        resp = access_client.patch(
            "/professors/550e8400-e29b-41d4-a716-446655440100",
            json={"first_name": "Editado"},
        )
        assert resp.status_code in (401, 403), resp.text

    def test_insufficient_role_returns_403(self, access_client):
        """Un usuario con rol `student` recibe 403 en una ruta de administrador."""
        token = create_access_token({"sub": STUDENT_EMAIL})
        resp = access_client.get(
            "/admin/stats",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403, resp.text
