"""
Pruebas de humo — el sistema arranca y responde tras un cambio/despliegue.

Nivel:   Sistema
Tipo:    Asociada al Cambio (Humo)
Técnica: Caja Negra
Objetivo: verificación mínima y rápida de que la app levanta y sus endpoints
          de salud responden. Se corre antes de una suite completa o de un deploy.

Bajo prueba: app/main.py + /health/db

TODO: implementar. Requiere fixture de cliente HTTP sobre la app.
"""
import pytest

pytestmark = pytest.mark.skip(reason="Pendiente de implementación")


class TestSmoke:
    async def test_app_starts(self):
        """La aplicación se instancia/levanta sin errores."""

    async def test_health_db_responds_200(self):
        """/health/db responde 200 (SELECT 1 a la base)."""

    async def test_openapi_available(self):
        """El esquema OpenAPI se sirve correctamente."""
