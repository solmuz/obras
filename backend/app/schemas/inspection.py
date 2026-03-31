from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


# External Inspection enums
class InspectionStatusEnum(str, Enum):
    """Inspection status - computed based on expiration date."""
    VIGENTE = "VIGENTE"
    VENCIDA = "VENCIDA"


class ExternalInspectionCompanyEnum(str, Enum):
    """Companies for external inspections."""
    GEO = "GEO"
    SBCIMAS = "SBCIMAS"
    PREFA = "PREFA"
    BESSAC = "BESSAC"


class ExternalInspectionCreate(BaseModel):
    """Request schema for creating an external inspection."""
    accessory_id: UUID
    inspection_date: datetime
    company: ExternalInspectionCompanyEnum
    company_responsible: str
    final_criterion: str
    certificate_number: Optional[str] = None
    project_name: str
    equipment_status: str

    class Config:
        json_schema_extra = {
            "example": {
                "accessory_id": "550e8400-e29b-41d4-a716-446655440000",
                "inspection_date": "2026-03-20T10:00:00",
                "company": "GEO",
                "company_responsible": "GEO Certificadora S.A.",
                "final_criterion": "APROBADO",
                "certificate_number": "CERT-2026-001",
                "project_name": "Proyecto Torre Central",
                "equipment_status": "EN_USO"
            }
        }


class ExternalInspectionUpdate(BaseModel):
    """Request schema for updating an external inspection."""
    company: Optional[ExternalInspectionCompanyEnum] = None
    company_responsible: Optional[str] = None
    final_criterion: Optional[str] = None
    certificate_number: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "company": "SBCIMAS",
                "final_criterion": "APROBADO CON OBSERVACIONES"
            }
        }


class ExternalInspectionOut(BaseModel):
    """Response schema for external inspection output."""
    id: UUID
    accessory_id: UUID
    inspection_date: datetime
    company: ExternalInspectionCompanyEnum
    company_responsible: str
    final_criterion: str
    next_inspection_date: datetime
    status: InspectionStatusEnum
    certificate_number: Optional[str]
    certificate_pdf: str  # File path/URL
    project_name: str
    equipment_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Site Inspection enums
class ColorPeriodEnum(str, Enum):
    """Bimonthly color-code inspection periods."""
    ENE_FEB = "ENE_FEB"
    MAR_ABR = "MAR_ABR"
    MAY_JUN = "MAY_JUN"
    JUL_AGO = "JUL_AGO"
    SEP_OCT = "SEP_OCT"
    NOV_DIC = "NOV_DIC"


class SiteInspectionResultEnum(str, Enum):
    """Result of on-site inspection."""
    BUEN_ESTADO = "BUEN_ESTADO"
    MAL_ESTADO = "MAL_ESTADO"
    OBSERVACIONES = "OBSERVACIONES"


class SiteInspectionCompanyEnum(str, Enum):
    """Companies for on-site inspections."""
    GEO = "GEO"
    SBCIMAS = "SBCIMAS"
    PREFA = "PREFA"
    BESSAC = "BESSAC"


class SiteInspectionCreate(BaseModel):
    """Request schema for creating a site inspection."""
    accessory_id: UUID
    inspection_date: datetime
    final_criterion: SiteInspectionResultEnum
    inspector_name: str
    company: SiteInspectionCompanyEnum
    project_name: str
    equipment_status: str
    photo_urls: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "accessory_id": "550e8400-e29b-41d4-a716-446655440000",
                "inspection_date": "2026-03-20T10:00:00",
                "final_criterion": "BUEN_ESTADO",
                "inspector_name": "Juan Pérez",
                "company": "GEO",
                "project_name": "Proyecto Torre Central",
                "equipment_status": "EN_USO"
            }
        }


class SiteInspectionUpdate(BaseModel):
    """Request schema for updating a site inspection."""
    final_criterion: Optional[SiteInspectionResultEnum] = None
    inspector_name: Optional[str] = None
    company: Optional[SiteInspectionCompanyEnum] = None
    photo_urls: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "final_criterion": "OBSERVACIONES",
                "inspector_name": "Carlos López"
            }
        }


class SiteInspectionOut(BaseModel):
    """Response schema for site inspection output."""
    id: UUID
    accessory_id: UUID
    inspection_date: datetime
    final_criterion: SiteInspectionResultEnum
    inspector_name: str
    company: SiteInspectionCompanyEnum
    color_period: ColorPeriodEnum
    next_inspection_date: datetime
    status: InspectionStatusEnum
    photo_urls: Optional[List[str]]
    project_name: str
    equipment_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
