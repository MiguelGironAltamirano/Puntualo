"""
Pruebas unitarias de core/security.py — hashing de contraseñas y JWT.

Nivel:   Unitaria
Tipo:    Funcional
Técnica: Caja Blanca
Objetivo: verificar las funciones criptográficas y de tokens de forma aislada.

Bajo prueba: app/core/security.py
"""
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify_password(self):
        """El hash de una contraseña se verifica correctamente contra el original."""
        password = "S3gur4-Contrasena!"
        hashed = hash_password(password)

        # El hash no es la contraseña en claro y tiene formato bcrypt.
        assert hashed != password
        assert hashed.startswith("$2")
        assert verify_password(password, hashed) is True

    def test_hash_is_salted_and_non_deterministic(self):
        """Dos hashes de la misma contraseña difieren (salt aleatorio) y ambos verifican."""
        password = "misma-contrasena"
        h1 = hash_password(password)
        h2 = hash_password(password)

        assert h1 != h2
        assert verify_password(password, h1)
        assert verify_password(password, h2)

    def test_wrong_password_fails_verification(self):
        """Una contraseña incorrecta no verifica contra el hash."""
        hashed = hash_password("la-correcta")

        assert verify_password("la-incorrecta", hashed) is False


class TestJWT:
    def test_create_access_token(self):
        """Se crea un access token con el payload y expiración esperados."""
        token = create_access_token({"sub": "user@unmsm.edu.pe", "role": "student"})

        assert isinstance(token, str)

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        assert payload["sub"] == "user@unmsm.edu.pe"
        assert payload["role"] == "student"
        assert payload["type"] == "access"
        # La expiración debe caer dentro de la ventana configurada (+/- 1 min).
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        assert abs((exp - expected).total_seconds()) < 60

    def test_refresh_token_marked_as_refresh(self):
        """El refresh token lleva type='refresh' y expira más tarde que el access."""
        token = create_refresh_token({"sub": "user@unmsm.edu.pe", "role": "student"})
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        assert payload["type"] == "refresh"

    def test_decode_valid_token(self):
        """Un token válido se decodifica y expone el subject/claims."""
        token = create_access_token({"sub": "someone@unmsm.edu.pe", "role": "admin"})

        payload = decode_token(token)

        assert payload is not None
        assert payload["sub"] == "someone@unmsm.edu.pe"
        assert payload["role"] == "admin"

    def test_expired_token_rejected(self):
        """Un token expirado es rechazado (decode_token -> None)."""
        expired = jwt.encode(
            {
                "sub": "user@unmsm.edu.pe",
                "type": "access",
                "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        assert decode_token(expired) is None

    def test_tampered_token_rejected(self):
        """Un token con firma alterada es rechazado (decode_token -> None)."""
        token = create_access_token({"sub": "user@unmsm.edu.pe"})

        # Alterar un carácter intermedio de la firma invalida el token. (Cambiar
        # el último carácter base64url no siempre altera los bytes de la firma
        # por los bits de relleno, por eso mutamos en el medio.)
        header, payload, signature = token.split(".")
        mid = len(signature) // 2
        flipped = "X" if signature[mid] != "X" else "Y"
        tampered_signature = signature[:mid] + flipped + signature[mid + 1:]
        tampered = ".".join([header, payload, tampered_signature])

        assert decode_token(tampered) is None

    def test_token_signed_with_other_key_rejected(self):
        """Un token firmado con otra clave secreta no se acepta."""
        foreign = jwt.encode(
            {"sub": "attacker@unmsm.edu.pe", "type": "access"},
            "otra-clave-distinta",
            algorithm=settings.ALGORITHM,
        )

        assert decode_token(foreign) is None
