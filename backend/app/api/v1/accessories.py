from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pathlib import Path
import logging

from app.db.session import get_db
from app.models.accessory import ElementTypeEnum, BrandEnum, UsageStatusEnum
from app.models.user import User
from app.schemas.accessory import (
    AccessoryCreate, AccessoryUpdate, AccessoryOut, AccessoryListOut
)
from app.services.accessory_service import AccessoryService
from app.services.audit_service import AuditService
from app.core.dependencies import get_current_user, require_admin, require_write_access
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/accessories", tags=["Accessories"])

# Photo storage directory
PHOTO_STORAGE_PATH = Path("storage/photos")
PHOTO_STORAGE_PATH.mkdir(parents=True, exist_ok=True)


@router.get("", response_model=list[AccessoryListOut], status_code=status.HTTP_200_OK)
async def list_accessories(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    project_id: UUID | None = Query(None),
    status_filter: UsageStatusEnum | None = Query(None, alias="status"),
    element_type: ElementTypeEnum | None = Query(None),
    brand: BrandEnum | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AccessoryListOut]:
    """
    List accessories with optional filtering.
    
    Args:
        skip: Pagination offset
        limit: Max results
        project_id: Filter by project
        status_filter: Filter by usage status
        element_type: Filter by element type
        brand: Filter by brand
        db: Database session
        current_user: Current user
        
    Returns:
        List of accessory summaries
    """
    try:
        accessories, _ = await AccessoryService.list_accessories(
            db=db, skip=skip, limit=limit, project_id=project_id,
            status=status_filter, element_type=element_type, brand=brand
        )
        return [AccessoryListOut.from_orm(a) for a in accessories]
    except Exception as e:
        logger.error(f"Error listing accessories: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.get("/{accessory_id}", response_model=AccessoryOut, status_code=status.HTTP_200_OK)
async def get_accessory(
    accessory_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AccessoryOut:
    """
    Get detailed accessory information.
    
    Args:
        accessory_id: Accessory ID
        db: Database session
        current_user: Current user
        
    Returns:
        Detailed accessory information
        
    Raises:
        HTTPException: If accessory not found
    """
    try:
        accessory = await AccessoryService.get_accessory_by_id(db, accessory_id)
        if not accessory:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Accessory not found")
        return AccessoryOut.from_orm(accessory)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting accessory: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.post("", response_model=AccessoryOut, status_code=status.HTTP_201_CREATED)
async def create_accessory(
    accessory_data: AccessoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write_access),
) -> AccessoryOut:
    """
    Create a new accessory (hoja de vida).
    
    Args:
        accessory_data: Accessory creation request
        db: Database session
        current_user: Current user
        
    Returns:
        Created accessory details
        
    Raises:
        HTTPException: If code_internal already exists or project not found
    """
    try:
        accessory = await AccessoryService.create_accessory(db, accessory_data)
        
        acc_out = AccessoryOut.from_orm(accessory)
        
        # Log audit trail
        await AuditService.log_create(
            db=db, entity_type="accessory", entity_id=accessory.id,
            new_values=acc_out.dict(),
            user_id=current_user.id, description="Created accessory"
        )
        
        return acc_out
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating accessory: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.patch("/{accessory_id}", response_model=AccessoryOut, status_code=status.HTTP_200_OK)
async def update_accessory(
    accessory_id: UUID,
    accessory_data: AccessoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write_access),
) -> AccessoryOut:
    """
    Update mutable accessory fields (project_id, status, photos).
    Immutable fields (code_internal, brand, type, serial, material, capacities, dimensions)
    are protected from modification.
    
    Args:
        accessory_id: Accessory ID to update
        accessory_data: Update request (mutable fields only)
        db: Database session
        current_user: Current user
        
    Returns:
        Updated accessory details
        
    Raises:
        HTTPException: If accessory not found or version conflict
    """
    try:
        old_accessory = await AccessoryService.get_accessory_by_id(db, accessory_id)
        if not old_accessory:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Accessory not found")
        
        old_values = AccessoryOut.from_orm(old_accessory).dict()
        
        accessory = await AccessoryService.update_accessory(db, accessory_id, accessory_data)
        acc_out = AccessoryOut.from_orm(accessory)
        
        # Log audit trail
        await AuditService.log_update(
            db=db, entity_type="accessory", entity_id=accessory_id,
            old_values=old_values, new_values=acc_out.dict(),
            user_id=current_user.id, description="Updated accessory"
        )
        
        return acc_out
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating accessory: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.delete("/{accessory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_accessory(
    accessory_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Soft-delete an accessory.
    
    Args:
        accessory_id: Accessory ID to delete
        db: Database session
        current_user: Current user
        
    Raises:
        HTTPException: If accessory not found
    """
    try:
        old_accessory = await AccessoryService.get_accessory_by_id(db, accessory_id)
        if not old_accessory:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Accessory not found")
        
        success = await AccessoryService.soft_delete_accessory(db, accessory_id)
        
        # Log audit trail
        await AuditService.log_delete(
            db=db, entity_type="accessory", entity_id=accessory_id,
            old_values=AccessoryOut.from_orm(old_accessory).dict(),
            user_id=current_user.id, description="Deleted accessory"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting accessory: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.post("/{accessory_id}/photos", status_code=status.HTTP_201_CREATED)
async def upload_accessory_photo(
    accessory_id: UUID,
    photo: UploadFile = File(...),
    photo_type: str = Query(..., description="Type: accessory, manufacturer_label, or provider_marking"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write_access),
) -> dict:
    """
    Upload a photo for an accessory.
    
    Args:
        accessory_id: Accessory ID
        photo: Image file upload
        photo_type: Type of photo (accessory, manufacturer_label, provider_marking)
        db: Database session
        current_user: Current user
        
    Returns:
        Photo upload confirmation with path
        
    Raises:
        HTTPException: If accessory not found or file invalid
    """
    try:
        accessory = await AccessoryService.get_accessory_by_id(db, accessory_id)
        if not accessory:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Accessory not found")
        
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
        
        # Save file using AccessoryService
        file_path = await AccessoryService.add_photo(db, accessory_id, photo, photo_type)
        
        # Log audit trail
        await AuditService.log_update(
            db=db, entity_type="accessory", entity_id=accessory_id,
            old_values={}, new_values={"photo_type": photo_type, "file_path": str(file_path)},
            user_id=current_user.id, description=f"Added photo: {photo_type}"
        )
        
        return {
            "file_path": str(file_path),
            "photo_type": photo_type,
            "message": "Photo uploaded successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading photo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e
