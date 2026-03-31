from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

from app.db.session import get_db
from app.models.audit_log import AuditLog, AuditActionEnum
from app.models.user import RoleEnum, User
from app.schemas.audit_log import AuditLogOut, AuditLogListOut
from app.services.audit_service import AuditService
from app.core.dependencies import get_current_user, get_current_user_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=list[AuditLogListOut], status_code=status.HTTP_200_OK)
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    entity_type: str | None = Query(None),
    action: AuditActionEnum | None = Query(None),
    user_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_role: RoleEnum = Depends(get_current_user_role),
) -> list[AuditLogListOut]:
    """
    List audit logs with role-based access control.
    
    Permission Model:
    - ADMIN: See all audit logs
    - INGENIERO_HSE: See only audit logs for entities they created or modified
    - CONSULTA: Cannot access audit logs (raises 403)
    
    Args:
        skip: Pagination offset
        limit: Max results
        entity_type: Filter by entity type (e.g., "accessory", "project", "user")
        action: Filter by action (CREATE, UPDATE, DELETE)
        user_id: Filter by user who made the change (ADMIN only)
        db: Database session
        current_user_id: Current authenticated user
        current_role: Current user's role
        
    Returns:
        List of audit log entries (compact view, no old/new values)
        
    Raises:
        HTTPException: If user lacks permission (403 for CONSULTA)
    """
    # RBAC: Check permission
    if current_role == RoleEnum.CONSULTA:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Audit log access denied for CONSULTA role",
        )
    
    # RBAC: INGENIERO_HSE can only see their own logs
    effective_user_id = user_id
    if current_role == RoleEnum.INGENIERO_HSE:
        effective_user_id = current_user.id

    try:
        logs, _ = await AuditService.list_logs(
            db=db, skip=skip, limit=limit, entity_type=entity_type, action=action,
            user_id=effective_user_id,
        )
        return [AuditLogListOut.from_orm(log) for log in logs]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing audit logs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.get("/{log_id}", response_model=AuditLogOut, status_code=status.HTTP_200_OK)
async def get_audit_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_role: RoleEnum = Depends(get_current_user_role),
) -> AuditLogOut:
    """
    Get detailed audit log entry including old/new values (JSON).
    
    Permission Model:
    - ADMIN: See any log
    - INGENIERO_HSE: See only logs where they are the user_id
    - CONSULTA: Cannot access (403)
    
    Args:
        log_id: Audit log ID
        db: Database session
        current_user_id: Current user
        current_role: Current user's role
        
    Returns:
        Detailed audit log with before/after values
        
    Raises:
        HTTPException: If log not found or permission denied
    """
    # RBAC: Check permission
    if current_role == RoleEnum.CONSULTA:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Audit log access denied for CONSULTA role",
        )
    
    try:
        log = await AuditService.get_log_by_id(db=db, log_id=log_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit log not found",
            )
        # RBAC: INGENIERO_HSE can only see entries they authored
        if current_role == RoleEnum.INGENIERO_HSE and log.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this audit log entry",
            )
        return AuditLogOut.from_orm(log)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit log: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.get("/by-entity/{entity_type}/{entity_id}", response_model=list[AuditLogOut], status_code=status.HTTP_200_OK)
async def get_entity_audit_history(
    entity_type: str,
    entity_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_role: RoleEnum = Depends(get_current_user_role),
) -> list[AuditLogOut]:
    """
    Get complete audit history for a specific entity.
    Shows all changes made to a single accessory, project, user, etc.
    
    Permission Model:
    - ADMIN: See audit history for any entity
    - INGENIERO_HSE: See only entities they created/modified
    - CONSULTA: Cannot access (403)
    
    Args:
        entity_type: Type of entity (e.g., "accessory", "project")
        entity_id: ID of the entity
        skip: Pagination offset
        limit: Max results
        db: Database session
        current_user_id: Current user
        current_role: Current user's role
        
    Returns:
        Ordered list of all changes to the entity (oldest first)
        
    Raises:
        HTTPException: If user lacks permission (403)
    """
    # RBAC: Check permission
    if current_role == RoleEnum.CONSULTA:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Audit log access denied for CONSULTA role",
        )
    
    try:
        all_logs = await AuditService.get_entity_history(
            db=db, entity_type=entity_type, entity_id=entity_id,
        )
        # RBAC: INGENIERO_HSE can only see entries they authored
        if current_role == RoleEnum.INGENIERO_HSE:
            all_logs = [log for log in all_logs if log.user_id == current_user.id]
        paginated = all_logs[skip: skip + limit]
        return [AuditLogOut.from_orm(log) for log in paginated]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.get("/by-user/{target_user_id}", response_model=list[AuditLogListOut], status_code=status.HTTP_200_OK)
async def get_user_audit_activity(
    target_user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    entity_type: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_role: RoleEnum = Depends(get_current_user_role),
) -> list[AuditLogListOut]:
    """
    Get all activities performed by a specific user.
    
    Permission Model:
    - ADMIN: See audit activity for any user
    - INGENIERO_HSE: See only their own activity (target_user_id must equal current_user_id)
    - CONSULTA: Cannot access (403)
    
    Args:
        target_user_id: User whose activities to retrieve
        skip: Pagination offset
        limit: Max results
        entity_type: Optional filter by entity type
        db: Database session
        current_user_id: Current user
        current_role: Current user's role
        
    Returns:
        List of audit logs for the target user's activities
        
    Raises:
        HTTPException: If permission denied
    """
    # RBAC: Check permission
    if current_role == RoleEnum.CONSULTA:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Audit log access denied for CONSULTA role",
        )
    
    if current_role == RoleEnum.INGENIERO_HSE and target_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own activity logs",
        )

    try:
        # Use list_logs so we can filter by both user_id and entity_type
        logs, _ = await AuditService.list_logs(
            db=db, user_id=target_user_id, entity_type=entity_type,
            skip=skip, limit=limit,
        )
        return [AuditLogListOut.from_orm(log) for log in logs]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user actions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e
