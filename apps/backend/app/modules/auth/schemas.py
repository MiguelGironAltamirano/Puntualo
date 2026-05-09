from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import field_validator


class RegisterRequest(BaseModel):

    email: EmailStr

    full_name: str

    password: str

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


class UserResponse(BaseModel):

    id: str

    email: EmailStr

    full_name: str

    role: str

    is_active: bool

    is_verified: bool

    provider: str

    model_config = {
        "from_attributes": True
    }