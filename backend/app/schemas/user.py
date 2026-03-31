from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

from app.core.config import PASSWORD_MIN_LENGTH, PASSWORD_PATTERN


class RoleEnum(str, Enum):
    """User role enumeration."""
    ADMIN = "ADMIN"
    INGENIERO_HSE = "INGENIERO_HSE"
    CONSULTA = "CONSULTA"


class UserCreate(BaseModel):
    """Request schema for creating a new user."""
    email: EmailStr
    full_name: str
    password: str
    role: RoleEnum = RoleEnum.CONSULTA

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < PASSWORD_MIN_LENGTH:
            raise ValueError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")
        if not PASSWORD_PATTERN.match(v):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character"
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "password": "SecurePass1!",
                "role": "INGENIERO_HSE"
            }
        }


class UserUpdate(BaseModel):
    """Request schema for updating a user."""
    full_name: Optional[str] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe Updated",
                "role": "ADMIN",
                "is_active": True
            }
        }


class UserOut(BaseModel):
    """Response schema for user output."""
    id: UUID
    email: str
    full_name: str
    role: RoleEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "role": "INGENIERO_HSE",
                "is_active": True,
                "created_at": "2026-03-20T10:00:00",
                "updated_at": "2026-03-20T10:00:00"
            }
        }


class UserListOut(BaseModel):
    """Response schema for listing users."""
    id: UUID
    email: str
    full_name: str
    role: RoleEnum
    is_active: bool

    class Config:
        from_attributes = True
