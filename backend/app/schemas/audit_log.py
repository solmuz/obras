from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class AuditActionEnum(str, Enum):
    """Audit trail action types."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class AuditLogOut(BaseModel):
    """Response schema for audit log output."""
    id: UUID
    user_id: Optional[UUID]
    entity_type: str
    entity_id: UUID
    action: AuditActionEnum
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    change_description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "entity_type": "accessory",
                "entity_id": "550e8400-e29b-41d4-a716-446655440000",
                "action": "UPDATE",
                "old_values": {
                    "status": "EN_USO"
                },
                "new_values": {
                    "status": "EN_STOCK"
                },
                "change_description": "Equipment status changed from EN_USO to EN_STOCK",
                "created_at": "2026-03-20T10:00:00"
            }
        }


class AuditLogListOut(BaseModel):
    """Response schema for listing audit logs."""
    id: UUID
    user_id: Optional[UUID]
    entity_type: str
    entity_id: UUID
    action: AuditActionEnum
    created_at: datetime

    class Config:
        from_attributes = True
