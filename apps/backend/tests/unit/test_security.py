"""
Pruebas unitarias de core/security.py — hashing de contraseñas y JWT.

Nivel:   Unitaria
Tipo:    Funcional
Técnica: Caja Blanca
Objetivo: verificar las funciones criptográficas y de tokens de forma aislada.

Bajo prueba: app/core/security.py

TODO: implementar. Casos previstos abajo (marcados como skip).
"""
import pytest

pytestmark = pytest.mark.skip(reason="Pendiente de implementación")


class TestPasswordHashing:
    async def test_hash_and_verify_password(self):
        """El hash de una contraseña se verifica correctamente contra el original."""

    async def test_wrong_password_fails_verification(self):
        """Una contraseña incorrecta no verifica contra el hash."""


class TestJWT:
    async def test_create_access_token(self):
        """Se crea un access token con el payload y expiración esperados."""

    async def test_decode_valid_token(self):
        """Un token válido se decodifica y expone el subject/claims."""

    async def test_expired_token_rejected(self):
        """Un token expirado lanza el error de credenciales correspondiente."""

    async def test_tampered_token_rejected(self):
        """Un token con firma alterada es rechazado."""
