"""
Pruebas de integración del flujo de autenticación (registro, login, refresh).

Nivel:   Integración
Tipo:    Funcional
Técnica: Caja Blanca
Objetivo: ejercitar los endpoints de auth contra la app + DB de prueba.

Bajo prueba: app/modules/auth/router.py, service.py

TODO: implementar. Requiere fixture de cliente HTTP (httpx.AsyncClient sobre la app).
"""
import pytest

pytestmark = pytest.mark.skip(reason="Pendiente de implementación")


class TestAuthAPI:
    async def test_register_new_user(self):
        """Un registro válido crea el usuario y responde 201."""

    async def test_login_valid_credentials_returns_token(self):
        """Login con credenciales correctas devuelve access token."""

    async def test_login_invalid_credentials_rejected(self):
        """Login con credenciales incorrectas devuelve 401."""

    async def test_refresh_token_flow(self):
        """El refresh token emite un nuevo access token válido."""
