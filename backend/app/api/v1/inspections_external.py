from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pathlib import Path
import logging

from app.db.session import get_db
from app.models.inspection_external import ExternalInspectionCompanyEnum, InspectionStatusEnum
from app.models.user import User
from app.schemas.inspection import (
    ExternalInspectionCreate, ExternalInspectionOut
)
from app.services.inspection_external_service import ExternalInspectionService
from app.services.audit_service import AuditService
from app.core.dependencies import get_current_user, require_admin, require_write_access
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inspections/external", tags=["External Inspections"])

# Certificate storage directory
CERT_STORAGE_PATH = Path("storage/certificates")
CERT_STORAGE_PATH.mkdir(parents=True, exist_ok=True)


@router.get("", response_model=list[ExternalInspectionOut], status_code=status.HTTP_200_OK)
async def list_external_inspections(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    accessory_id: UUID | None = Query(None),
    company: ExternalInspectionCompanyEnum | None = Query(None),
    status_filter: InspectionStatusEnum | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ExternalInspectionOut]:
    """
    List external inspections with optional filtering.
    
    Args:
        skip: Pagination offset
        limit: Max results
        accessory_id: Filter by accessory
        company: Filter by inspection company
        status_filter: Filter by inspection status (VIGENTE/VENCIDA)
        db: Database session
        current_user: Current user
        
    Returns:
        List of external inspection records
    """
    try:
        inspections, _ = await ExternalInspectionService.list_inspections(
            db=db, skip=skip, limit=limit, accessory_id=accessory_id,
            company=company, status=status_filter
        )
        return [ExternalInspectionOut.from_orm(i) for i in inspections]
    except Exception as e:
        logger.error(f"Error listing external inspections: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.get("/{inspection_id}", response_model=ExternalInspectionOut, status_code=status.HTTP_200_OK)
async def get_external_inspection(
    inspection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExternalInspectionOut:
    """
    Get detailed external inspection record.
    
    Args:
        inspection_id: Inspection ID
        db: Database session
        current_user: Current user
        
    Returns:
        Detailed inspection information
        
    Raises:
        HTTPException: If inspection not found
    """
    try:
        inspection = await ExternalInspectionService.get_inspection_by_id(db, inspection_id)
        if not inspection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
        return ExternalInspectionOut.from_orm(inspection)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting external inspection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.post("", response_model=ExternalInspectionOut, status_code=status.HTTP_201_CREATED)
async def create_external_inspection(
    inspection_data: ExternalInspectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write_access),
) -> ExternalInspectionOut:
    """
    Create a new external inspection record (6-month cycle).
    
    Automatically calculates next_inspection_date (inspection_date + 180 days)
    and status (VIGENTE if next_date > today, else VENCIDA).
    
    Args:
        inspection_data: Inspection creation request
        db: Database session
        current_user: Current user
        
    Returns:
        Created inspection record
        
    Raises:
        HTTPException: If accessory not found
    """
    try:
        inspection = await ExternalInspectionService.create_inspection(db, inspection_data)
        insp_out = ExternalInspectionOut.from_orm(inspection)
        
        # Log audit trail
        await AuditService.log_create(
            db=db, entity_type="external_inspection", entity_id=inspection.id,
            new_values=insp_out.dict(),
            user_id=current_user.id, description="Created external inspection"
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
        logger.error(f"Error creating external inspection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.patch("/{inspection_id}", response_model=ExternalInspectionOut, status_code=status.HTTP_200_OK)
async def update_external_inspection(
    inspection_id: UUID,
    inspection_data: ExternalInspectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write_access),
) -> ExternalInspectionOut:
    """
    Update an external inspection record with optimistic locking.
    
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
        old_inspection = await ExternalInspectionService.get_inspection_by_id(db, inspection_id)
        if not old_inspection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
        
        old_values = ExternalInspectionOut.from_orm(old_inspection).dict()
        
        inspection = await ExternalInspectionService.update_inspection(db, inspection_id, inspection_data)
        insp_out = ExternalInspectionOut.from_orm(inspection)
        
        # Log audit trail
        await AuditService.log_update(
            db=db, entity_type="external_inspection", entity_id=inspection_id,
            old_values=old_values, new_values=insp_out.dict(),
            user_id=current_user.id, description="Updated external inspection"
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
        logger.error(f"Error updating external inspection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.delete("/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_external_inspection(
    inspection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Soft-delete an external inspection record.
    
    Args:
        inspection_id: Inspection ID to delete
        db: Database session
        current_user: Current user
        
    Raises:
        HTTPException: If inspection not found
    """
    try:
        old_inspection = await ExternalInspectionService.get_inspection_by_id(db, inspection_id)
        if not old_inspection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
        
        success = await ExternalInspectionService.soft_delete_inspection(db, inspection_id)
        
        # Log audit trail
        await AuditService.log_delete(
            db=db, entity_type="external_inspection", entity_id=inspection_id,
            old_values=ExternalInspectionOut.from_orm(old_inspection).dict(),
            user_id=current_user.id, description="Deleted external inspection"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting external inspection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.post("/{inspection_id}/certificate", status_code=status.HTTP_201_CREATED)
async def upload_certificate(
    inspection_id: UUID,
    certificate: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Upload a PDF certificate for an external inspection.
    
    Args:
        inspection_id: Inspection ID
        certificate: PDF file upload
        db: Database session
        current_user: Current user
        
    Returns:
        Certificate upload confirmation with path
        
    Raises:
        HTTPException: If inspection not found or file invalid
    """
    try:
        inspection = await ExternalInspectionService.get_external_inspection_by_id(db, inspection_id)
        if not inspection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
        
        # Validate file type
        if certificate.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only PDF files are allowed",
            )
        
        # Validate file size
        file_size_mb = len(await certificate.read()) / (1024 * 1024)
        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Max file size: {settings.MAX_FILE_SIZE_MB}MB",
            )
        await certificate.seek(0)  # Reset file pointer
        
        # Save file using service
        file_path = await ExternalInspectionService.add_certificate(db, inspection_id, certificate)
        
        # Log audit trail
        await AuditService.log_update(
            db=db, entity_type="external_inspection", entity_id=inspection_id,
            old_values={}, new_values={"certificate_pdf": str(file_path)},
            user_id=current_user.id, description="Added certificate"
        )
        
        return {
            "file_path": str(file_path),
            "message": "Certificate uploaded successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading certificate: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e
