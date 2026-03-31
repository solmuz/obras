from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class DecommissionCreate(BaseModel):
    """Request schema for creating a decommission record (Acta de Baja)."""
    accessory_id: UUID
    decommission_date: datetime
    reason: str
    responsible_name: str
    photo_urls: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "accessory_id": "550e8400-e29b-41d4-a716-446655440000",
                "decommission_date": "2026-03-20T10:00:00",
                "reason": "Rotura en ramal principal después de inspección",
                "responsible_name": "Carlos López"
            }
        }


class DecommissionUpdate(BaseModel):
    """Request schema for updating a decommission record."""
    reason: Optional[str] = None
    responsible_name: Optional[str] = None
    photo_urls: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "reason": "Rotura en ramal principal - reparación no viable"
            }
        }


class DecommissionOut(BaseModel):
    """Response schema for decommission record output."""
    id: UUID
    accessory_id: UUID
    decommission_date: datetime
    reason: str
    responsible_name: str
    photo_urls: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "accessory_id": "550e8400-e29b-41d4-a716-446655440000",
                "decommission_date": "2026-03-20T10:00:00",
                "reason": "Rotura en ramal principal después de inspección",
                "responsible_name": "Carlos López",
                "photo_urls": [
                    "/storage/photos/decomm-001.jpg",
                    "/storage/photos/decomm-002.jpg"
                ],
                "created_at": "2026-03-20T10:00:00",
                "updated_at": "2026-03-20T10:00:00"
            }
        }
