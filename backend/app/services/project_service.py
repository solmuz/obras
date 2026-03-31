"""Project management service - CRUD and employee assignment."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete, func
from datetime import datetime, timezone
import logging

from app.models.project import Project, ProjectStatusEnum, project_users
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for project management including employee assignment."""

    @staticmethod
    async def get_project_by_id(db: AsyncSession, project_id: UUID) -> Optional[Project]:
        """
        Get project by ID (active projects only).

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            Project object or None if not found
        """
        stmt = select(Project).where(
            and_(
                Project.id == project_id,
                Project.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_project_by_name(db: AsyncSession, name: str) -> Optional[Project]:
        """
        Get project by name (active projects only).

        Args:
            db: Database session
            name: Project name

        Returns:
            Project object or None if not found
        """
        stmt = select(Project).where(
            and_(
                Project.name == name,
                Project.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_projects(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProjectStatusEnum] = None,
    ) -> tuple[List[Project], int]:
        """
        List projects with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Max records to return
            status: Filter by status (optional)

        Returns:
            Tuple of (list of projects, total count)
        """
        # Build filter conditions
        conditions = [Project.deleted_at.is_(None)]
        if status is not None:
            conditions.append(Project.status == status)

        # Count query
        count_result = await db.execute(
            select(func.count()).select_from(Project).where(and_(*conditions))
        )
        total_count = count_result.scalar() or 0

        # Data query
        stmt = select(Project).where(and_(*conditions)).offset(skip).limit(limit)
        result = await db.execute(stmt)
        projects = result.scalars().all()

        return projects, total_count

    @staticmethod
    async def create_project(
        db: AsyncSession,
        project_create: ProjectCreate,
        created_by_id: UUID,
    ) -> Project:
        """
        Create a new project.

        Args:
            db: Database session
            project_create: Project creation schema
            created_by_id: ID of user creating the project

        Returns:
            Created project object
        """
        project = Project(
            name=project_create.name,
            description=project_create.description,
            status=project_create.status,
            start_date=project_create.start_date,
            created_by=created_by_id,
        )

        db.add(project)
        await db.commit()
        await db.refresh(project)

        logger.info(f"Created project: {project.name}")
        return project

    @staticmethod
    async def update_project(
        db: AsyncSession,
        project_id: UUID,
        project_update: ProjectUpdate,
    ) -> Optional[Project]:
        """
        Update project information.

        Args:
            db: Database session
            project_id: Project ID
            project_update: Project update schema

        Returns:
            Updated project object or None if not found
        """
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            return None

        # Update fields if provided
        if project_update.name is not None:
            project.name = project_update.name
        if project_update.description is not None:
            project.description = project_update.description
        if project_update.status is not None:
            project.status = project_update.status

        project.updated_at = datetime.now(timezone.utc)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        logger.info(f"Updated project: {project.name}")
        return project

    @staticmethod
    async def assign_employee(
        db: AsyncSession,
        project_id: UUID,
        user_id: UUID,
    ) -> Project:
        """
        Assign an employee to a project.

        Args:
            db: Database session
            project_id: Project ID
            user_id: User ID (employee)

        Returns:
            Updated project

        Raises:
            ValueError: If project not found, user not found, or already assigned
        """
        # Verify project exists
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Verify user exists and is active
        user_stmt = select(User).where(
            and_(
                User.id == user_id,
                User.deleted_at.is_(None),
                User.is_active.is_(True)
            )
        )
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User {user_id} not found or not active")

        # Check if already assigned (and not removed)
        assign_stmt = select(project_users).where(
            and_(
                project_users.c.project_id == project_id,
                project_users.c.user_id == user_id,
                project_users.c.fecha_remocion.is_(None)
            )
        )
        assign_result = await db.execute(assign_stmt)
        if assign_result.scalar_one_or_none():
            raise ValueError(f"User {user_id} already assigned to project {project_id}")

        # Assign employee
        stmt = project_users.insert().values(
            project_id=project_id,
            user_id=user_id,
            fecha_asignacion=datetime.now(timezone.utc),
        )
        await db.execute(stmt)
        await db.commit()

        logger.info(f"Assigned user {user_id} to project {project_id}")
        
        # Return updated project
        return await ProjectService.get_project_by_id(db, project_id)

    @staticmethod
    async def remove_employee(
        db: AsyncSession,
        project_id: UUID,
        user_id: UUID,
    ) -> Project:
        """
        Remove an employee from a project (soft remove).

        Args:
            db: Database session
            project_id: Project ID
            user_id: User ID (employee)

        Returns:
            Updated project

        Raises:
            ValueError: If project not found or user not assigned
        """
        # Verify project exists
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Verify assignment exists
        assign_stmt = select(project_users).where(
            and_(
                project_users.c.project_id == project_id,
                project_users.c.user_id == user_id,
                project_users.c.fecha_remocion.is_(None)
            )
        )
        assign_result = await db.execute(assign_stmt)
        assignment = assign_result.mappings().first()

        if not assignment:
            raise ValueError(f"User {user_id} not assigned to project {project_id}")

        # Update removal date
        update_stmt = (
            project_users.update()
            .where(
                and_(
                    project_users.c.project_id == project_id,
                    project_users.c.user_id == user_id,
                )
            )
            .values(fecha_remocion=datetime.now(timezone.utc))
        )
        await db.execute(update_stmt)
        await db.commit()

        logger.info(f"Removed user {user_id} from project {project_id}")
        
        # Return updated project
        return await ProjectService.get_project_by_id(db, project_id)

    @staticmethod
    async def get_project_employees(
        db: AsyncSession,
        project_id: UUID,
    ) -> List[User]:
        """
        Get all currently assigned employees for a project.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            List of currently assigned employees
        """
        stmt = (
            select(User)
            .join(project_users)
            .where(
                and_(
                    project_users.c.project_id == project_id,
                    project_users.c.fecha_remocion.is_(None),
                    User.deleted_at.is_(None),
                    User.is_active.is_(True)
                )
            )
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_project_employee_count(
        db: AsyncSession,
        project_id: UUID,
    ) -> int:
        """
        Get count of currently assigned employees for a project.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            Count of employees
        """
        stmt = select(func.count()).select_from(project_users).where(
            and_(
                project_users.c.project_id == project_id,
                project_users.c.fecha_remocion.is_(None),
            )
        )
        result = await db.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    async def soft_delete_project(db: AsyncSession, project_id: UUID) -> bool:
        """
        Soft delete a project.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            True if successful, False if project not found
        """
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            return False

        project.deleted_at = datetime.now(timezone.utc)
        db.add(project)
        await db.commit()

        logger.info(f"Soft deleted project: {project.name}")
        return True

    @staticmethod
    async def hard_delete_project(db: AsyncSession, project_id: UUID) -> bool:
        """
        Hard delete a project and all its records.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            True if successful, False if project not found
        """
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            return False

        await db.delete(project)
        await db.commit()

        logger.info(f"Hard deleted project: {project.name}")
        return True

    @staticmethod
    async def restore_project(db: AsyncSession, project_id: UUID) -> Optional[Project]:
        """
        Restore a soft-deleted project.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            Restored project or None if not found
        """
        stmt = select(Project).where(Project.id == project_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()

        if not project:
            return None

        project.deleted_at = None
        db.add(project)
        await db.commit()
        await db.refresh(project)

        logger.info(f"Restored project: {project.name}")
        return project
