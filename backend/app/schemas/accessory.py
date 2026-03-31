from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class BrandEnum(str, Enum):
    """Equipment brand enumeration."""
    BRAND_1 = "BRAND_1"
    BRAND_2 = "BRAND_2"
    BRAND_3 = "BRAND_3"


class ElementTypeEnum(str, Enum):
    """Type of lifting accessory."""
    ESLINGAS = "ESLINGAS"
    GRILLETES = "GRILLETES"
    GANCHOS = "GANCHOS"
    OTROS = "OTROS"


class UsageStatusEnum(str, Enum):
    """Equipment usage status."""
    EN_USO = "EN_USO"
    EN_STOCK = "EN_STOCK"
    TAG_ROJO = "TAG_ROJO"


class AccessoryCreate(BaseModel):
    """Request schema for creating an accessory."""
    code_internal: str
    element_type: ElementTypeEnum
    brand: BrandEnum
    serial: str
    material: str
    capacity_vertical: Optional[str] = None
    capacity_choker: Optional[str] = None
    capacity_basket: Optional[str] = None
    length_m: Optional[float] = None
    diameter_inches: Optional[str] = None
    num_ramales: Optional[int] = None
    project_id: UUID
    status: UsageStatusEnum = UsageStatusEnum.EN_USO

    class Config:
        json_schema_extra = {
            "example": {
                "code_internal": "ACC-001",
                "element_type": "ESLINGAS",
                "brand": "BRAND_1",
                "serial": "SN123456",
                "material": "Nylon",
                "capacity_vertical": "V: 2 TON",
                "capacity_choker": "C: 1.6 TON",
                "capacity_basket": "B: 3 TON",
                "length_m": 1.5,
                "diameter_inches": "1/2",
                "num_ramales": 4,
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "EN_USO"
            }
        }


class AccessoryUpdate(BaseModel):
    """Request schema for updating an accessory."""
    project_id: Optional[UUID] = None
    status: Optional[UsageStatusEnum] = None
    photo_accessory: Optional[str] = None
    photo_manufacturer_label: Optional[str] = None
    photo_provider_marking: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "EN_STOCK",
                "photo_accessory": "/storage/photos/ACC-001-main.jpg"
            }
        }


class AccessoryOut(BaseModel):
    """Response schema for accessory output."""
    id: UUID
    code_internal: str
    element_type: ElementTypeEnum
    brand: BrandEnum
    serial: str
    material: str
    capacity_vertical: Optional[str]
    capacity_choker: Optional[str]
    capacity_basket: Optional[str]
    length_m: Optional[float]
    diameter_inches: Optional[str]
    num_ramales: Optional[int]
    project_id: UUID
    status: UsageStatusEnum
    photo_accessory: Optional[str]
    photo_manufacturer_label: Optional[str]
    photo_provider_marking: Optional[str]
    version: int
    created_at: datetime
    updated_at: datetime
    semaforo_status: str = "VERDE"  # Computed field

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "code_internal": "ACC-001",
                "element_type": "ESLINGAS",
                "brand": "BRAND_1",
                "serial": "SN123456",
                "material": "Nylon",
                "capacity_vertical": "V: 2 TON",
                "capacity_choker": "C: 1.6 TON",
                "capacity_basket": "B: 3 TON",
                "length_m": 1.5,
                "diameter_inches": "1/2",
                "num_ramales": 4,
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "EN_USO",
                "photo_accessory": "/storage/photos/ACC-001-main.jpg",
                "photo_manufacturer_label": "/storage/photos/ACC-001-label.jpg",
                "photo_provider_marking": "/storage/photos/ACC-001-marking.jpg",
                "version": 1,
                "created_at": "2026-03-20T10:00:00",
                "updated_at": "2026-03-20T10:00:00",
                "semaforo_status": "VERDE"
            }
        }


class AccessoryListOut(BaseModel):
    """Response schema for listing accessories (compact view)."""
    id: UUID
    code_internal: str
    element_type: ElementTypeEnum
    brand: BrandEnum
    status: UsageStatusEnum
    semaforo_status: str = "VERDE"

    class Config:
        from_attributes = True
