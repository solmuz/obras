from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

from app.db.session import get_db
from app.models.project import ProjectStatusEnum
from app.models.user import User
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectOut, ProjectDetailOut,
    AssignEmployeeRequest, RemoveEmployeeRequest
)
from app.services.project_service import ProjectService
from app.services.audit_service import AuditService
from app.core.dependencies import get_current_user, require_admin, require_write_access

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectOut], status_code=status.HTTP_200_OK)
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: ProjectStatusEnum | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectOut]:
    """
    List all active projects with optional filtering by status.
    
    Args:
        skip: Offset for pagination
        limit: Max results per page
        status_filter: Filter by project status (ACTIVO/INACTIVO)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of project summaries with accessory counts
    """
    try:
        projects, _ = await ProjectService.list_projects(
            db=db, skip=skip, limit=limit, status=status_filter
        )
        return [ProjectOut.from_orm(p) for p in projects]
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.get("/{project_id}", response_model=ProjectDetailOut, status_code=status.HTTP_200_OK)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectDetailOut:
    """
    Get project details including assigned employees.
    
    Args:
        project_id: Project ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Detailed project information with employee list
        
    Raises:
        HTTPException: If project not found
    """
    try:
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return ProjectDetailOut.from_orm(project)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write_access),
) -> ProjectOut:
    """
    Create a new project.
    
    Args:
        project_data: Project creation request
        db: Database session
        current_user: Current authenticated user (becomes creator)
        
    Returns:
        Created project details
        
    Raises:
        HTTPException: If project name already exists
    """
    try:
        project = await ProjectService.create_project(db, project_data, created_by_id=current_user.id)
        proj_out = ProjectOut.from_orm(project)
        
        # Log audit trail
        await AuditService.log_create(
            db=db, entity_type="project", entity_id=project.id,
            new_values=ProjectOut.from_orm(project).dict(),
            user_id=current_user.id, description="Created project"
        )
        
        return proj_out
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.patch("/{project_id}", response_model=ProjectOut, status_code=status.HTTP_200_OK)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write_access),
) -> ProjectOut:
    """
    Update project information.
    
    Args:
        project_id: Project ID to update
        project_data: Update request (partial fields)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated project details
        
    Raises:
        HTTPException: If project not found
    """
    try:
        old_project = await ProjectService.get_project_by_id(db, project_id)
        if not old_project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
        old_values = ProjectOut.from_orm(old_project).dict()
        
        project = await ProjectService.update_project(db, project_id, project_data)
        proj_out = ProjectOut.from_orm(project)
        
        # Log audit trail
        await AuditService.log_update(
            db=db, entity_type="project", entity_id=project_id,
            old_values=old_values, new_values=proj_out.dict(),
            user_id=current_user.id, description="Updated project"
        )
        
        return proj_out
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Soft-delete a project (mark as deleted).
    
    Args:
        project_id: Project ID to delete
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If project not found
    """
    try:
        old_project = await ProjectService.get_project_by_id(db, project_id)
        if not old_project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
        success = await ProjectService.soft_delete_project(db, project_id)
        
        # Log audit trail
        await AuditService.log_delete(
            db=db, entity_type="project", entity_id=project_id,
            old_values=ProjectOut.from_orm(old_project).dict(),
            user_id=current_user.id, description="Deleted project"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.post("/{project_id}/assign-employee", response_model=ProjectDetailOut, status_code=status.HTTP_200_OK)
async def assign_employee_to_project(
    project_id: UUID,
    request: AssignEmployeeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ProjectDetailOut:
    """
    Assign an employee to a project.
    
    Args:
        project_id: Project ID
        request: Assignment request with user_id
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated project with new employee
        
    Raises:
        HTTPException: If project or user not found
    """
    try:
        project = await ProjectService.assign_employee(db, project_id, request.user_id)
        
        # Log audit trail
        await AuditService.log_create(
            db=db, entity_type="project_employee", entity_id=project_id,
            new_values={"user_id": str(request.user_id)},
            user_id=current_user.id, description=f"Assigned employee {request.user_id}"
        )
        
        return ProjectDetailOut.from_orm(project)
    except ValueError as e:
        # Specific validation errors from service
        error_msg = str(e)
        if "already assigned" in error_msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning employee: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e


@router.delete("/{project_id}/employees/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_employee_from_project(
    project_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Remove an employee from a project.
    
    Args:
        project_id: Project ID
        user_id: User ID to remove
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If project not found or user not assigned
    """
    try:
        project = await ProjectService.remove_employee(db, project_id, user_id)
        
        # Log audit trail
        await AuditService.log_delete(
            db=db, entity_type="project_employee", entity_id=project_id,
            old_values={"user_id": str(user_id)},
            user_id=current_user.id, description=f"Removed employee {user_id}"
        )
    except ValueError as e:
        # Specific validation errors from service
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing employee: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error") from e
