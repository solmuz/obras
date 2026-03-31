from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pathlib import Path
from datetime import datetime
import logging
import io

from app.db.session import get_db
from app.models.user import User
from app.models.accessory import Accessory, ElementTypeEnum, BrandEnum, UsageStatusEnum
from app.models.inspection_external import ExternalInspection, InspectionStatusEnum
from app.models.inspection_site import SiteInspection
from app.schemas.accessory import AccessoryListOut
from app.services.report_service import ReportService
from app.core.dependencies import get_current_user
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])

# PDF export storage directory
PDF_STORAGE_PATH = Path("storage/reports")
PDF_STORAGE_PATH.mkdir(parents=True, exist_ok=True)


@router.get("/semaforo", response_model=list[AccessoryListOut], status_code=status.HTTP_200_OK)
async def get_semaforo_report(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    semaforo_status: str | None = Query(None, description="VERDE, AMARILLO, or ROJO"),
    project_id: UUID | None = Query(None),
    element_type: ElementTypeEnum | None = Query(None),
    brand: BrandEnum | None = Query(None),
    usage_status: UsageStatusEnum | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AccessoryListOut]:
    """
    Get semáforo status report for all accessories.
    
    Semáforo Logic (Color based on inspection cycles):
    - VERDE (Green): Both external and site inspections are VIGENTE
    - AMARILLO (Yellow): One inspection is VENCIDA or missing
    - ROJO (Red): Equipment has been decommissioned (acta de baja) OR multiple inspections VENCIDA
    
    Filtering by semaforo_status allows categorization of equipment by inspection status.
    
    Args:
        skip: Pagination offset
        limit: Max results
        semaforo_status: Filter by color (VERDE, AMARILLO, ROJO)
        project_id: Filter by project
        element_type: Filter by equipment type
        brand: Filter by brand
        usage_status: Filter by usage status
        db: Database session
        current_user_id: Current user
        
    Returns:
        List of accessories with semáforo status computed
    """
    try:
        result = await ReportService.get_global_semaforo_summary(
            db=db, skip=skip, limit=limit, semaforo_status=semaforo_status,
            project_id=project_id, element_type=element_type, brand=brand, usage_status=usage_status
        )
        return result
    except Exception as e:
        logger.error(f"Error getting semaforo report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.get("/semaforo/by-project/{project_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_project_semaforo_summary(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get semáforo summary for a specific project.
    
    Returns count and list of equipment in each color category.
    
    Args:
        project_id: Project ID
        db: Database session
        current_user_id: Current user
        
    Returns:
        Summary with verde_count, amarillo_count, rojo_count, and lists per color
    """
    try:
        result = await ReportService.get_project_semaforo_summary(db=db, project_id=project_id)
        return result
    except Exception as e:
        logger.error(f"Error getting project semaforo summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.post("/export-pdf", status_code=status.HTTP_201_CREATED)
async def export_semaforo_pdf(
    semaforo_status: str | None = Query(None),
    project_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    """
    Export semáforo report as PDF file.
    
    Generates a PDF document with semáforo color summary and detailed equipment list.
    Requires: pip install reportlab
    
    Args:
        semaforo_status: Filter by color (optional)
        project_id: Filter by project (optional)
        db: Database session
        current_user_id: Current user
        
    Returns:
        PDF file with semáforo report
        
    Raises:
        HTTPException: If reportlab not installed
    """
    try:
        result = await ReportService.export_semaforo_pdf(
            db=db, semaforo_status=semaforo_status, project_id=project_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e

