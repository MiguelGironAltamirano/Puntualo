"""
Pruebas de integración del flujo de autenticación (registro, login, refresh).

Nivel:   Integración
Tipo:    Funcional
Técnica: Caja Blanca
Objetivo: ejercitar los endpoints de auth contra la app + DB de prueba.

Bajo prueba: app/modules/auth/router.py, service.py

El registro real es en dos pasos: POST /auth/register envía un código por correo
y POST /auth/register/verify crea el usuario (201). En pruebas mockeamos el envío
de correo y fijamos el código de verificación para poder completar el flujo.
"""
from datetime import datetime, timezone

import pytest

import app.modules.auth.service as auth_service

FIXED_CODE = "123456"
USER_EMAIL = "nuevo.alumno@unmsm.edu.pe"
USER_PASSWORD = "Contrasena-Segura1"


@pytest.fixture(autouse=True)
def _stub_email_and_code(monkeypatch):
    """Evita SMTP real y fija el código de verificación a un valor conocido."""
    monkeypatch.setattr(auth_service, "send_email", lambda *a, **k: None)
    monkeypatch.setattr(auth_service, "_generate_verification_code", lambda: FIXED_CODE)


@pytest.fixture(autouse=True)
def _naive_utc_clock(monkeypatch):
    """SQLite descarta el tzinfo de los DateTime; usamos UTC naive de forma
    consistente en el servicio para que las comparaciones de expiración de los
    códigos no mezclen naive/aware. No altera la lógica, solo el reloj."""

    class _NaiveUTCDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.now(timezone.utc).replace(tzinfo=None)

    monkeypatch.setattr(auth_service, "datetime", _NaiveUTCDatetime)


def _register_and_verify(client, email=USER_EMAIL, username="nuevo_alumno"):
    """Helper: completa el flujo de alta y devuelve la respuesta del verify (201)."""
    start = client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Nuevo Alumno",
            "password": USER_PASSWORD,
            "username": username,
        },
    )
    assert start.status_code == 200, start.text

    return client.post(
        "/auth/register/verify",
        json={"email": email, "code": FIXED_CODE},
    )


class TestAuthAPI:
    def test_register_new_user(self, api_client):
        """Un registro válido (start + verify) crea el usuario y responde 201."""
        resp = _register_and_verify(api_client)

        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["email"] == USER_EMAIL
        assert body["username"] == "nuevo_alumno"
        assert body["role"] == "student"

    def test_register_non_institutional_email_rejected(self, api_client):
        """El correo debe ser institucional UNMSM; otro dominio -> 422."""
        resp = api_client.post(
            "/auth/register",
            json={
                "email": "persona@gmail.com",
                "full_name": "Persona Externa",
                "password": USER_PASSWORD,
                "username": "externa",
            },
        )
        assert resp.status_code == 422

    def test_register_duplicate_email_rejected(self, api_client):
        """Registrar un correo ya dado de alta -> 400."""
        _register_and_verify(api_client)

        resp = api_client.post(
            "/auth/register",
            json={
                "email": USER_EMAIL,
                "full_name": "Otro Nombre",
                "password": USER_PASSWORD,
                "username": "otro_usuario",
            },
        )
        assert resp.status_code == 400

    def test_login_valid_credentials_returns_token(self, api_client):
        """CP-API-02 · Integración · Pruebas de API · Ninguno · Usuario registrado y verificado · 1. POST /login con credenciales correctas · 200 OK + access y refresh token"""
        _register_and_verify(api_client)

        resp = api_client.post(
            "/auth/login",
            json={"email": USER_EMAIL, "password": USER_PASSWORD},
        )

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["access_token"]
        assert body["refresh_token"]
        assert body["token_type"] == "bearer"
        assert body["role"] == "student"

    def test_login_invalid_password_rejected(self, api_client):
        """CP-API-03 · Integración · Pruebas de API · Ninguno · Usuario registrado · 1. POST /login con contraseña incorrecta · 401 Unauthorized"""
        _register_and_verify(api_client)

        resp = api_client.post(
            "/auth/login",
            json={"email": USER_EMAIL, "password": "no-es-la-clave"},
        )
        assert resp.status_code == 401

    def test_login_unknown_user_rejected(self, api_client):
        """Login de un correo inexistente devuelve 401."""
        resp = api_client.post(
            "/auth/login",
            json={"email": "fantasma@unmsm.edu.pe", "password": "x"},
        )
        assert resp.status_code == 401

    def test_refresh_token_flow(self, api_client):
        """El refresh token emite un nuevo access token válido."""
        _register_and_verify(api_client)
        login = api_client.post(
            "/auth/login",
            json={"email": USER_EMAIL, "password": USER_PASSWORD},
        )
        refresh_token = login.json()["refresh_token"]

        resp = api_client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["access_token"]
        assert body["token_type"] == "bearer"

    def test_refresh_with_invalid_token_rejected(self, api_client):
        """Un refresh token inválido devuelve 401."""
        resp = api_client.post(
            "/auth/refresh",
            json={"refresh_token": "token-basura"},
        )
        assert resp.status_code == 401

    def test_me_requires_authentication(self, api_client):
        """El endpoint protegido /auth/me sin token devuelve 401/403."""
        resp = api_client.get("/auth/me")
        assert resp.status_code in (401, 403)

    def test_me_returns_current_user_with_token(self, api_client):
        """Con un access token válido, /auth/me devuelve el usuario autenticado."""
        _register_and_verify(api_client)
        login = api_client.post(
            "/auth/login",
            json={"email": USER_EMAIL, "password": USER_PASSWORD},
        )
        access_token = login.json()["access_token"]

        resp = api_client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["email"] == USER_EMAIL
