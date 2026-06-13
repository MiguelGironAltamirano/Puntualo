import uuid
from uuid import UUID

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import field_validator


class RegisterRequest(BaseModel):

    email: EmailStr

    full_name: str

    password: str

    username: str

    dni: str | None = None

    career_id: int | None = None

    @field_validator("email")
    @classmethod
    def validate_unmsm_email(
        cls,
        value: str
    ) -> str:

        if not value.endswith("@unmsm.edu.pe"):

            raise ValueError(
                "Solo se permiten correos institucionales UNMSM"
            )

        return value.lower()


class LoginRequest(BaseModel):

    email: EmailStr

    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        value: str
    ) -> str:

        return value.lower()


class TokenResponse(BaseModel):

    access_token: str

    refresh_token: str

    token_type: str = "bearer"

    role: str


class RegisterStartResponse(BaseModel):

    detail: str

    expires_in_seconds: int


class RegisterVerifyRequest(BaseModel):

    email: EmailStr

    code: str

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        value: str
    ) -> str:

        return value.lower()

    @field_validator("code")
    @classmethod
    def validate_code(
        cls,
        value: str
    ) -> str:

        if len(value) != 6 or not value.isdigit():
            raise ValueError("Codigo invalido")

        return value


class PasswordResetStartRequest(BaseModel):

    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        value: str
    ) -> str:

        return value.lower()


class PasswordResetStartResponse(BaseModel):

    detail: str

    expires_in_seconds: int


class PasswordResetVerifyRequest(BaseModel):

    email: EmailStr

    code: str

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        value: str
    ) -> str:

        return value.lower()

    @field_validator("code")
    @classmethod
    def validate_code(
        cls,
        value: str
    ) -> str:

        if len(value) != 6 or not value.isdigit():
            raise ValueError("Codigo invalido")

        return value


class PasswordResetConfirmRequest(BaseModel):

    email: EmailStr

    code: str

    new_password: str

    confirm_password: str

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        value: str
    ) -> str:

        return value.lower()

    @field_validator("code")
    @classmethod
    def validate_code(
        cls,
        value: str
    ) -> str:

        if len(value) != 6 or not value.isdigit():
            raise ValueError("Codigo invalido")

        return value


class PasswordResetConfirmResponse(BaseModel):

    detail: str


class UserResponse(BaseModel):

    id: UUID

    email: EmailStr

    full_name: str

    username: str

    dni: str | None = None

    career_id: int | None = None

    role: str

    is_active: bool

    is_verified: bool

    provider: str

    model_config = {
        "from_attributes": True
    }

    @field_validator("id", mode="before")
    @classmethod
    def coerce_uuid_to_str(cls, v: object) -> str:
        return str(v) if isinstance(v, uuid.UUID) else v
    
class RefreshTokenRequest(BaseModel):
    refresh_token: str