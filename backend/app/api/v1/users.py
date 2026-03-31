from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import logging

from app.db.session import get_db
from app.models.user import User, RoleEnum
from app.schemas.user import UserCreate, UserUpdate, UserOut, UserListOut
from app.core.dependencies import get_current_user, require_admin
from app.services.user_service import UserService
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserListOut], status_code=status.HTTP_200_OK)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[RoleEnum] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[UserListOut]:
    """
    List all active users with optional filtering.
    
    Args:
        skip: Number of users to skip (pagination)
        limit: Maximum number of users to return
        role: Filter by role (optional)
        is_active: Filter by active status (optional)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of user summaries
    """
    try:
        users, _ = await UserService.list_users(
            db=db,
            skip=skip,
            limit=limit,
            role=role,
            is_active=is_active,
        )
        return [UserListOut.from_orm(u) for u in users]
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing users",
        ) from e


@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserOut:
    """
    Get a specific user by ID.
    
    Args:
        user_id: User ID to retrieve
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        User details
        
    Raises:
        HTTPException: If user not found
    """
    user = await UserService.get_user_by_id_active(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserOut.from_orm(user)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserOut:
    """
    Create a new user (ADMIN only).
    
    Args:
        user_data: User creation request
        db: Database session
        current_user: Current admin user
        
    Returns:
        Created user details
        
    Raises:
        HTTPException: If email already exists
    """
    try:
        # Check if email already exists
        existing = await UserService.get_user_by_email(db, user_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        
        user = await UserService.create_user(db, user_data)
        
        # Log audit
        await AuditService.log_create(
            db=db,
            entity_type="user",
            entity_id=user.id,
            new_values=UserOut.from_orm(user).dict(),
            user_id=current_user.id,
            description=f"Created user {user.email}",
        )
        
        return UserOut.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user",
        ) from e


@router.patch("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserOut:
    """
    Update a user (ADMIN only).
    
    Args:
        user_id: User ID to update
        user_data: User update request (partial)
        db: Database session
        current_user: Current admin user
        
    Returns:
        Updated user details
        
    Raises:
        HTTPException: If user not found
    """
    try:
        old_user = await UserService.get_user_by_id_active(db, user_id)
        if not old_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        old_values = UserOut.from_orm(old_user).dict()
        
        user = await UserService.update_user(db, user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        new_values = UserOut.from_orm(user).dict()
        
        # Log audit
        await AuditService.log_update(
            db=db,
            entity_type="user",
            entity_id=user.id,
            old_values=old_values,
            new_values=new_values,
            user_id=current_user.id,
            description=f"Updated user {user.email}",
        )
        
        return UserOut.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user",
        ) from e


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> None:
    """
    Soft delete a user (ADMIN only).
    
    Args:
        user_id: User ID to delete
        db: Database session
        current_user: Current admin user
        
    Raises:
        HTTPException: If user not found
    """
    try:
        old_user = await UserService.get_user_by_id_active(db, user_id)
        if not old_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        old_values = UserOut.from_orm(old_user).dict()
        
        success = await UserService.soft_delete_user(db, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # Log audit
        await AuditService.log_delete(
            db=db,
            entity_type="user",
            entity_id=user_id,
            old_values=old_values,
            user_id=current_user.id,
            description=f"Deleted user {old_user.email}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user",
        ) from e
