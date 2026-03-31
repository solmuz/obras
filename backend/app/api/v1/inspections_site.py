from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pathlib import Path
import logging

from app.db.session import get_db
from app.models.inspection_site import (
    ColorPeriodEnum, SiteInspectionResultEnum,
    InspectionStatusEnum
)
from app.models.user import User
from app.schemas.inspection import (
    SiteInspectionCreate, SiteInspectionOut
)
from app.services.inspection_site_service import SiteInspectionService
from app.services.audit_service import AuditService
from app.core.dependencies import get_current_user, require_admin, require_write_access
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inspections/site", tags=["Site Inspections"])

# Photo storage directory
PHOTO_STORAGE_PATH = Path("storage/site_inspection_photos")
PHOTO_STORAGE_PATH.mkdir(parents=True, exist_ok=True)


@router.get("", response_model=list[SiteInspectionOut], status_code=status.HTTP_200_OK)
async def list_site_inspections(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    accessory_id: UUID | None = Query(None),
    color_period: ColorPeriodEnum | None = Query(None),
    result_filter: SiteInspectionResultEnum | None = Query(None, alias="result"),
    status_filter: InspectionStatusEnum | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SiteInspectionOut]:
    """
    List site inspections with optional filtering by color period, result, or status.
    
    Args:
        skip: Pagination offset
        limit: Max results
        accessory_id: Filter by accessory
        color_period: Filter by color period (bimonthly period)
        result_filter: Filter by inspection result
        status_filter: Filter by status (VIGENTE/VENCIDA)
        db: Database session
        current_user: Current user
        
    Returns:
        List of site inspection records
    """
    try:
        inspections, _ = await SiteInspectionService.list_inspections(
            db=db, skip=skip, limit=limit, accessory_id=accessory_id,
            color_period=color_period, status=status_filter
        )
        return [SiteInspectionOut.from_orm(i) for i in inspections]
    except Exception as e:
        logger.error(f"Error listing site inspections: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.get("/{inspection_id}", response_model=SiteInspectionOut, status_code=status.HTTP_200_OK)
async def get_site_inspection(
    inspection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SiteInspectionOut:
    """
    Get detailed site inspection record.
    
    Args:
        inspection_id: Inspection ID
        db: Database session
        current_user: Current user
        
    Returns:
        Detailed inspection information with photos
        
    Raises:
        HTTPException: If inspection not found
    """
    try:
        inspection = await SiteInspectionService.get_inspection_by_id(db, inspection_id)
        if not inspection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
        return SiteInspectionOut.from_orm(inspection)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting site inspection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.post("", response_model=SiteInspectionOut, status_code=status.HTTP_201_CREATED)
async def create_site_inspection(
    inspection_data: SiteInspectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write_access),
) -> SiteInspectionOut:
    """
    Create a new site inspection record (2-month cycle).
    
    Automatically calculates:
    - color_period: Bimonthly period based on inspection_date month
    - next_inspection_date: inspection_date + 60 days
    - status: VIGENTE if next_date > today, else VENCIDA
    
    Args:
        inspection_data: Inspection creation request
        db: Database session
        current_user: Current user
        
    Returns:
        Created site inspection record
        
    Raises:
        HTTPException: If accessory not found
    """
    try:
        inspection = await SiteInspectionService.create_inspection(db, inspection_data)
        insp_out = SiteInspectionOut.from_orm(inspection)
        
        # Log audit trail
        await AuditService.log_create(
            db=db, entity_type="site_inspection", entity_id=inspection.id,
            new_values=insp_out.dict(),
            user_id=current_user.id, description="Created site inspection"
        )
        
        return insp_out
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating site inspection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.patch("/{inspection_id}", response_model=SiteInspectionOut, status_code=status.HTTP_200_OK)
async def update_site_inspection(
    inspection_id: UUID,
    inspection_data: SiteInspectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write_access),
) -> SiteInspectionOut:
    """
    Update a site inspection record with optimistic locking.
    
    Recalculates color_period and next_inspection_date based on new inspection_date.
    
    Args:
        inspection_id: Inspection ID to update
        inspection_data: Update request
        db: Database session
        current_user: Current user
        
    Returns:
        Updated inspection record
        
    Raises:
        HTTPException: If inspection not found or version conflict
    """
    try:
        old_inspection = await SiteInspectionService.get_inspection_by_id(db, inspection_id)
        if not old_inspection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
        
        old_values = SiteInspectionOut.from_orm(old_inspection).dict()
        
        inspection = await SiteInspectionService.update_inspection(db, inspection_id, inspection_data)
        insp_out = SiteInspectionOut.from_orm(inspection)
        
        # Log audit trail
        await AuditService.log_update(
            db=db, entity_type="site_inspection", entity_id=inspection_id,
            old_values=old_values, new_values=insp_out.dict(),
            user_id=current_user.id, description="Updated site inspection"
        )
        
        return insp_out
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating site inspection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.delete("/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site_inspection(
    inspection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Soft-delete a site inspection record.
    
    Args:
        inspection_id: Inspection ID to delete
        db: Database session
        current_user: Current user
        
    Raises:
        HTTPException: If inspection not found
    """
    try:
        old_inspection = await SiteInspectionService.get_inspection_by_id(db, inspection_id)
        if not old_inspection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
        
        success = await SiteInspectionService.soft_delete_inspection(db, inspection_id)
        
        # Log audit trail
        await AuditService.log_delete(
            db=db, entity_type="site_inspection", entity_id=inspection_id,
            old_values=SiteInspectionOut.from_orm(old_inspection).dict(),
            user_id=current_user.id, description="Deleted site inspection"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting site inspection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.post("/{inspection_id}/photos", status_code=status.HTTP_201_CREATED)
async def upload_inspection_photo(
    inspection_id: UUID,
    photo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write_access),
) -> dict:
    """
    Upload a photo for a site inspection.
    
    Photos are stored as an array of file paths in the inspection record.
    
    Args:
        inspection_id: Inspection ID
        photo: Image file upload
        db: Database session
        current_user: Current user
        
    Returns:
        Photo upload confirmation with path
        
    Raises:
        HTTPException: If inspection not found or file invalid
    """
    try:
        inspection = await SiteInspectionService.get_site_inspection_by_id(db, inspection_id)
        if not inspection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
        
        # Validate file type
        if photo.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Allowed types: {settings.ALLOWED_IMAGE_TYPES}",
            )
        
        # Validate file size
        file_size_mb = len(await photo.read()) / (1024 * 1024)
        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Max file size: {settings.MAX_FILE_SIZE_MB}MB",
            )
        await photo.seek(0)  # Reset file pointer
        
        # Save file using service
        file_path = await SiteInspectionService.add_photo(db, inspection_id, photo)
        
        # Log audit trail
        await AuditService.log_update(
            db=db, entity_type="site_inspection", entity_id=inspection_id,
            old_values={}, new_values={"photo_path": str(file_path)},
            user_id=current_user.id, description="Added photo"
        )
        
        return {
            "file_path": str(file_path),
            "message": "Photo uploaded successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading photo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e
