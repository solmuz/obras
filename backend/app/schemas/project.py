from pydantic import BaseModel, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

from app.schemas.user import UserOut


class ProjectStatusEnum(str, Enum):
    """Project status enumeration."""
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"


class ProjectCreate(BaseModel):
    """Request schema for creating a project."""
    name: str
    description: Optional[str] = None
    status: ProjectStatusEnum = ProjectStatusEnum.ACTIVO
    start_date: datetime

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        """Convert status to uppercase for case-insensitive validation."""
        if isinstance(v, str):
            return v.upper()
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Proyecto Torre Central",
                "description": "Construcción de torre de 30 pisos",
                "status": "ACTIVO",
                "start_date": "2026-03-20T00:00:00"
            }
        }


class ProjectUpdate(BaseModel):
    """Request schema for updating a project."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatusEnum] = None

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        """Convert status to uppercase for case-insensitive validation."""
        if isinstance(v, str):
            return v.upper()
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Proyecto Torre Central - Actualizado",
                "status": "INACTIVO"
            }
        }


class AssignEmployeeRequest(BaseModel):
    """Request schema for assigning an employee to a project."""
    user_id: UUID

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class RemoveEmployeeRequest(BaseModel):
    """Request schema for removing an employee from a project."""
    user_id: UUID

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class ProjectOut(BaseModel):
    """Response schema for project output."""
    id: UUID
    name: str
    description: Optional[str]
    status: ProjectStatusEnum
    start_date: datetime
    created_at: datetime
    updated_at: datetime
    employee_count: int = 0
    accessory_count: int = 0

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Proyecto Torre Central",
                "description": "Construcción de torre de 30 pisos",
                "status": "ACTIVO",
                "start_date": "2026-03-20T00:00:00",
                "created_at": "2026-03-20T10:00:00",
                "updated_at": "2026-03-20T10:00:00",
                "employee_count": 5,
                "accessory_count": 25
            }
        }


class ProjectDetailOut(BaseModel):
    """Detailed response schema for project with employees and accessories."""
    id: UUID
    name: str
    description: Optional[str]
    status: ProjectStatusEnum
    start_date: datetime
    created_at: datetime
    updated_at: datetime
    employees: List[UserOut] = []  # List of assigned employees
    accessory_count: int = 0

    class Config:
        from_attributes = True
