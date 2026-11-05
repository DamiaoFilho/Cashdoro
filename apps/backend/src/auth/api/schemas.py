from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator

BCRYPT_MAX_PASSWORD_BYTES = 72
USERNAME_MAX_LENGTH = 50


class RegisterRequest(BaseModel):
    email: EmailStr
    username: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=USERNAME_MAX_LENGTH)
    ]
    password: str = Field(min_length=1)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, password: str) -> str:
        if len(password.encode()) > BCRYPT_MAX_PASSWORD_BYTES:
            raise ValueError(f"must be at most {BCRYPT_MAX_PASSWORD_BYTES} bytes")
        return password


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    username: str
    is_active: bool
    is_verified: bool
