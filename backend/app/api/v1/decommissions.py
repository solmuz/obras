from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pathlib import Path
from datetime import datetime, timezone
import logging

from app.db.session import get_db
from app.models.user import User
from app.models.decommission import DecommissionRecord
from app.models.accessory import Accessory, UsageStatusEnum
from app.schemas.decommission import DecommissionCreate, DecommissionOut
from app.services.decommission_service import DecommissionService
from app.services.audit_service import AuditService
from app.core.dependencies import get_current_user, require_admin, require_write_access
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/decommissions", tags=["Decommissions"])

# Photo storage directory
PHOTO_STORAGE_PATH = Path("storage/decommission_photos")
PHOTO_STORAGE_PATH.mkdir(parents=True, exist_ok=True)


@router.get("", response_model=list[DecommissionOut], status_code=status.HTTP_200_OK)
async def list_decommissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    accessory_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DecommissionOut]:
    """
    List decommission records (acta de baja) with optional filtering.
    
    Args:
        skip: Pagination offset
        limit: Max results
        accessory_id: Filter by accessory
        db: Database session
        current_user: Current user
        
    Returns:
        List of decommission records
    """
    try:
        decommissions, _ = await DecommissionService.list_records(
            db=db, skip=skip, limit=limit
        )
        return [DecommissionOut.from_orm(d) for d in decommissions]
    except Exception as e:
        logger.error(f"Error listing decommissions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.get("/{decommission_id}", response_model=DecommissionOut, status_code=status.HTTP_200_OK)
async def get_decommission(
    decommission_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DecommissionOut:
    """
    Get detailed decommission record.
    
    Args:
        decommission_id: Decommission ID
        db: Database session
        current_user: Current user
        
    Returns:
        Detailed decommission information
        
    Raises:
        HTTPException: If decommission not found
    """
    try:
        decommission = await DecommissionService.get_record_by_id(db, decommission_id)
        if not decommission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decommission not found",
            )
        return DecommissionOut.from_orm(decommission)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting decommission: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.post("", response_model=DecommissionOut, status_code=status.HTTP_201_CREATED)
async def create_decommission(
    decommission_data: DecommissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write_access),
) -> DecommissionOut:
    """
    Create a decommission record (acta de baja).
    
    This operation is ATOMIC:
    1. Verifies only one decommission per accessory
    2. Creates the DecommissionRecord
    3. Sets accessory status to TAG_ROJO (red tag)
    
    Transactional behavior ensures consistency.
    
    Args:
        decommission_data: Decommission creation request
        db: Database session
        current_user: Current user
        
    Returns:
        Created decommission record
        
    Raises:
        HTTPException: If accessory not found or already decommissioned
    """
    try:
        decommission = await DecommissionService.create_record(db, decommission_data)
        decommission_out = DecommissionOut.from_orm(decommission)
        await AuditService.log_create(
            db=db, entity_type="decommission", entity_id=decommission.id,
            new_values=decommission_out.dict(),
            user_id=current_user.id, description="Created decommission record"
        )
        return decommission_out
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating decommission: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.patch("/{decommission_id}", response_model=DecommissionOut, status_code=status.HTTP_200_OK)
async def update_decommission(
    decommission_id: UUID,
    decommission_data: DecommissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write_access),
) -> DecommissionOut:
    """
    Update a decommission record (reason, responsible, date).
    
    Args:
        decommission_id: Decommission ID to update
        decommission_data: Update request
        db: Database session
        current_user: Current user
        
    Returns:
        Updated decommission record
        
    Raises:
        HTTPException: If decommission not found
    """
    try:
        old_decommission = await DecommissionService.get_record_by_id(db, decommission_id)
        if not old_decommission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decommission not found",
            )
        
        decommission = await DecommissionService.update_record(db, decommission_id, decommission_data)
        decommission_out = DecommissionOut.from_orm(decommission)
        old_values = DecommissionOut.from_orm(old_decommission).dict()
        
        await AuditService.log_update(
            db=db, entity_type="decommission", entity_id=decommission_id,
            old_values=old_values, new_values=decommission_out.dict(),
            user_id=current_user.id, description="Updated decommission record"
        )
        return decommission_out
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating decommission: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.delete("/{decommission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_decommission(
    decommission_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Soft-delete a decommission record.
    
    NOTE: This does NOT revert the accessory status from TAG_ROJO.
    To reinstate an accessory, manually update its status in the accessories endpoint.
    
    Args:
        decommission_id: Decommission ID to delete
        db: Database session
        current_user: Current user
        
    Raises:
        HTTPException: If decommission not found
    """
    try:
        old_decommission = await DecommissionService.get_record_by_id(db, decommission_id)
        if not old_decommission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decommission not found",
            )
        
        await DecommissionService.soft_delete_record(db, decommission_id)
        old_values = DecommissionOut.from_orm(old_decommission).dict()
        
        await AuditService.log_delete(
            db=db, entity_type="decommission", entity_id=decommission_id,
            old_values=old_values,
            user_id=current_user.id, description="Deleted decommission record"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting decommission: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.post("/{decommission_id}/photos", status_code=status.HTTP_201_CREATED)
async def upload_decommission_photo(
    decommission_id: UUID,
    photo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write_access),
) -> dict:
    """
    Upload a photo for a decommission record.
    
    Photos are stored as an array of file paths.
    
    Args:
        decommission_id: Decommission ID
        photo: Image file upload
        db: Database session
        current_user: Current user
        
    Returns:
        Photo upload confirmation with path
        
    Raises:
        HTTPException: If decommission not found or file invalid
    """
    try:
        result = await DecommissionService.add_photo(db, decommission_id, photo)
        
        await AuditService.log_create(
            db=db, entity_type="decommission_photo", entity_id=decommission_id,
            new_values={"file_path": result["file_path"]},
            user_id=current_user.id, description="Uploaded decommission photo"
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading photo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e
