"""
Pruebas de integración de control de acceso (autorización de endpoints).

Nivel:   Integración
Tipo:    No Funcional (Seguridad)
Técnica: Caja Negra
Objetivo: confirmar que las rutas protegidas exigen token y rol adecuado.

Bajo prueba: dependencias de auth aplicadas a los routers protegidos.

TODO: implementar. Requiere fixture de cliente HTTP.
"""
import pytest

pytestmark = pytest.mark.skip(reason="Pendiente de implementación")


class TestAccessControl:
    async def test_protected_route_without_token_returns_401(self):
        """/professors sin token devuelve 401."""

    async def test_write_endpoint_without_token_returns_401(self):
        """Un endpoint de escritura sin token devuelve 401."""

    async def test_insufficient_role_returns_403(self):
        """Un usuario sin rol admin recibe 403 en rutas de admin."""
