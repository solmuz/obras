"""Accessory management service - CRUD and photo handling."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timezone
import logging

from app.models.accessory import Accessory, UsageStatusEnum, ElementTypeEnum, BrandEnum
from app.models.project import Project
from app.schemas.accessory import AccessoryCreate, AccessoryUpdate

logger = logging.getLogger(__name__)


class AccessoryService:
    """Service for accessory management including photo handling."""

    @staticmethod
    async def get_accessory_by_id(db: AsyncSession, accessory_id: UUID) -> Optional[Accessory]:
        """
        Get accessory by ID (active accessories only).

        Args:
            db: Database session
            accessory_id: Accessory ID

        Returns:
            Accessory object or None if not found
        """
        stmt = select(Accessory).where(
            and_(
                Accessory.id == accessory_id,
                Accessory.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_accessory_by_code(db: AsyncSession, code_internal: str) -> Optional[Accessory]:
        """
        Get accessory by internal code (active only).

        Args:
            db: Database session
            code_internal: Internal equipment code

        Returns:
            Accessory object or None if not found
        """
        stmt = select(Accessory).where(
            and_(
                Accessory.code_internal == code_internal,
                Accessory.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_accessories(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        project_id: Optional[UUID] = None,
        status: Optional[UsageStatusEnum] = None,
        element_type: Optional[ElementTypeEnum] = None,
        brand: Optional[BrandEnum] = None,
    ) -> tuple[List[Accessory], int]:
        """
        List accessories with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Max records to return
            project_id: Filter by project (optional)
            status: Filter by usage status (optional)
            element_type: Filter by element type (optional)
            brand: Filter by brand (optional)

        Returns:
            Tuple of (list of accessories, total count)
        """
        # Build filter conditions
        conditions = [Accessory.deleted_at.is_(None)]
        
        if project_id is not None:
            conditions.append(Accessory.project_id == project_id)
        if status is not None:
            conditions.append(Accessory.status == status)
        if element_type is not None:
            conditions.append(Accessory.element_type == element_type)
        if brand is not None:
            conditions.append(Accessory.brand == brand)

        # Count query
        count_result = await db.execute(
            select(func.count()).select_from(Accessory).where(and_(*conditions))
        )
        total_count = count_result.scalar() or 0

        # Data query
        stmt = select(Accessory).where(and_(*conditions)).offset(skip).limit(limit)
        result = await db.execute(stmt)
        accessories = result.scalars().all()

        return accessories, total_count

    @staticmethod
    async def create_accessory(
        db: AsyncSession,
        accessory_create: AccessoryCreate,
    ) -> Accessory:
        """
        Create a new accessory.

        Args:
            db: Database session
            accessory_create: Accessory creation schema

        Returns:
            Created accessory object

        Raises:
            ValueError: If project not found or code already exists
        """
        # Verify project exists
        project_stmt = select(Project).where(
            and_(
                Project.id == accessory_create.project_id,
                Project.deleted_at.is_(None)
            )
        )
        project_result = await db.execute(project_stmt)
        if not project_result.scalar_one_or_none():
            raise ValueError(f"Project {accessory_create.project_id} not found")

        # Check code uniqueness
        existing = await AccessoryService.get_accessory_by_code(db, accessory_create.code_internal)
        if existing:
            raise ValueError(f"Accessory code {accessory_create.code_internal} already exists")

        # Create accessory
        accessory = Accessory(
            code_internal=accessory_create.code_internal,
            element_type=accessory_create.element_type,
            brand=accessory_create.brand,
            serial=accessory_create.serial,
            material=accessory_create.material,
            capacity_vertical=accessory_create.capacity_vertical,
            capacity_choker=accessory_create.capacity_choker,
            capacity_basket=accessory_create.capacity_basket,
            length_m=accessory_create.length_m,
            diameter_inches=accessory_create.diameter_inches,
            num_ramales=accessory_create.num_ramales,
            project_id=accessory_create.project_id,
            status=accessory_create.status,
        )

        db.add(accessory)
        await db.commit()
        await db.refresh(accessory)

        logger.info(f"Created accessory: {accessory.code_internal} ({accessory.element_type})")
        return accessory

    @staticmethod
    async def update_accessory(
        db: AsyncSession,
        accessory_id: UUID,
        accessory_update: AccessoryUpdate,
    ) -> Optional[Accessory]:
        """
        Update accessory information (mutable fields only).

        Args:
            db: Database session
            accessory_id: Accessory ID
            accessory_update: Accessory update schema

        Returns:
            Updated accessory object or None if not found
        """
        accessory = await AccessoryService.get_accessory_by_id(db, accessory_id)
        if not accessory:
            return None

        # Verify new project exists if updating
        if accessory_update.project_id is not None:
            project_stmt = select(Project).where(
                and_(
                    Project.id == accessory_update.project_id,
                    Project.deleted_at.is_(None)
                )
            )
            project_result = await db.execute(project_stmt)
            if not project_result.scalar_one_or_none():
                logger.warning(f"Project {accessory_update.project_id} not found")
                return None
            accessory.project_id = accessory_update.project_id

        # Update mutable fields
        if accessory_update.status is not None:
            accessory.status = accessory_update.status
        if accessory_update.photo_accessory is not None:
            accessory.photo_accessory = accessory_update.photo_accessory
        if accessory_update.photo_manufacturer_label is not None:
            accessory.photo_manufacturer_label = accessory_update.photo_manufacturer_label
        if accessory_update.photo_provider_marking is not None:
            accessory.photo_provider_marking = accessory_update.photo_provider_marking

        accessory.updated_at = datetime.now(timezone.utc)
        # Increment version for optimistic locking
        accessory.version += 1

        db.add(accessory)
        await db.commit()
        await db.refresh(accessory)

        logger.info(f"Updated accessory: {accessory.code_internal}")
        return accessory

    @staticmethod
    async def add_photo(
        db: AsyncSession,
        accessory_id: UUID,
        photo_type: str,
        photo_path: str,
    ) -> Optional[Accessory]:
        """
        Add or update a photo for an accessory.

        Args:
            db: Database session
            accessory_id: Accessory ID
            photo_type: Type of photo ('accessory', 'manufacturer_label', 'provider_marking')
            photo_path: Path/URL to the photo

        Returns:
            Updated accessory object or None if not found
        """
        accessory = await AccessoryService.get_accessory_by_id(db, accessory_id)
        if not accessory:
            return None

        # Update appropriate photo field
        if photo_type == "accessory":
            accessory.photo_accessory = photo_path
        elif photo_type == "manufacturer_label":
            accessory.photo_manufacturer_label = photo_path
        elif photo_type == "provider_marking":
            accessory.photo_provider_marking = photo_path
        else:
            logger.warning(f"Unknown photo type: {photo_type}")
            return None

        accessory.updated_at = datetime.now(timezone.utc)
        db.add(accessory)
        await db.commit()
        await db.refresh(accessory)

        logger.info(f"Added {photo_type} photo to accessory {accessory.code_internal}")
        return accessory

    @staticmethod
    async def get_accessories_by_project(
        db: AsyncSession,
        project_id: UUID,
    ) -> List[Accessory]:
        """
        Get all accessories in a project.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            List of accessories
        """
        stmt = select(Accessory).where(
            and_(
                Accessory.project_id == project_id,
                Accessory.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_accessories_by_status(
        db: AsyncSession,
        status: UsageStatusEnum,
    ) -> List[Accessory]:
        """
        Get all accessories with a given status.

        Args:
            db: Database session
            status: Usage status

        Returns:
            List of accessories
        """
        stmt = select(Accessory).where(
            and_(
                Accessory.status == status,
                Accessory.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def soft_delete_accessory(db: AsyncSession, accessory_id: UUID) -> bool:
        """
        Soft delete an accessory.

        Args:
            db: Database session
            accessory_id: Accessory ID

        Returns:
            True if successful, False if not found
        """
        accessory = await AccessoryService.get_accessory_by_id(db, accessory_id)
        if not accessory:
            return False

        accessory.deleted_at = datetime.now(timezone.utc)
        db.add(accessory)
        await db.commit()

        logger.info(f"Soft deleted accessory: {accessory.code_internal}")
        return True

    @staticmethod
    async def hard_delete_accessory(db: AsyncSession, accessory_id: UUID) -> bool:
        """
        Hard delete an accessory.

        Args:
            db: Database session
            accessory_id: Accessory ID

        Returns:
            True if successful, False if not found
        """
        accessory = await AccessoryService.get_accessory_by_id(db, accessory_id)
        if not accessory:
            return False

        await db.delete(accessory)
        await db.commit()

        logger.info(f"Hard deleted accessory: {accessory.code_internal}")
        return True

    @staticmethod
    async def restore_accessory(db: AsyncSession, accessory_id: UUID) -> Optional[Accessory]:
        """
        Restore a soft-deleted accessory.

        Args:
            db: Database session
            accessory_id: Accessory ID

        Returns:
            Restored accessory or None if not found
        """
        stmt = select(Accessory).where(Accessory.id == accessory_id)
        result = await db.execute(stmt)
        accessory = result.scalar_one_or_none()

        if not accessory:
            return None

        accessory.deleted_at = None
        db.add(accessory)
        await db.commit()
        await db.refresh(accessory)

        logger.info(f"Restored accessory: {accessory.code_internal}")
        return accessory
