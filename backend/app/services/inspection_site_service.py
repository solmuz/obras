"""Site inspection service - MOD-06 on-site color-code inspections."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta, timezone
import logging

from app.models.inspection_site import (
    SiteInspection,
    ColorPeriodEnum,
    SiteInspectionResultEnum,
    SiteInspectionCompanyEnum,
    InspectionStatusEnum,
)
from app.models.accessory import Accessory
from app.schemas.inspection import (
    SiteInspectionCreate,
    SiteInspectionUpdate,
)

logger = logging.getLogger(__name__)


class SiteInspectionService:
    """Service for on-site color-code inspections - MOD-06."""

    @staticmethod
    async def get_inspection_by_id(
        db: AsyncSession,
        inspection_id: UUID,
    ) -> Optional[SiteInspection]:
        """
        Get site inspection by ID (active only).

        Args:
            db: Database session
            inspection_id: Inspection ID

        Returns:
            Inspection object or None if not found
        """
        stmt = select(SiteInspection).where(
            and_(
                SiteInspection.id == inspection_id,
                SiteInspection.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_inspections(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        accessory_id: Optional[UUID] = None,
        status: Optional[InspectionStatusEnum] = None,
        color_period: Optional[ColorPeriodEnum] = None,
        company: Optional[SiteInspectionCompanyEnum] = None,
    ) -> tuple[List[SiteInspection], int]:
        """
        List site inspections with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Max records to return
            accessory_id: Filter by accessory (optional)
            status: Filter by status (optional)
            color_period: Filter by color period (optional)
            company: Filter by company (optional)

        Returns:
            Tuple of (list of inspections, total count)
        """
        # Build filter conditions
        conditions = [SiteInspection.deleted_at.is_(None)]
        
        if accessory_id is not None:
            conditions.append(SiteInspection.accessory_id == accessory_id)
        if status is not None:
            conditions.append(SiteInspection.status == status)
        if color_period is not None:
            conditions.append(SiteInspection.color_period == color_period)
        if company is not None:
            conditions.append(SiteInspection.company == company)

        # Count query
        count_result = await db.execute(
            select(func.count()).select_from(SiteInspection).where(and_(*conditions))
        )
        total_count = count_result.scalar() or 0

        # Data query
        stmt = (
            select(SiteInspection)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        inspections = result.scalars().all()

        return inspections, total_count

    @staticmethod
    async def create_inspection(
        db: AsyncSession,
        inspection_create: SiteInspectionCreate,
    ) -> SiteInspection:
        """
        Create a new site inspection record.

        Args:
            db: Database session
            inspection_create: Inspection creation schema

        Returns:
            Created inspection object

        Raises:
            ValueError: If accessory not found
        """
        # Verify accessory exists
        accessory_stmt = select(Accessory).where(
            and_(
                Accessory.id == inspection_create.accessory_id,
                Accessory.deleted_at.is_(None)
            )
        )
        accessory_result = await db.execute(accessory_stmt)
        accessory = accessory_result.scalar_one_or_none()
        if not accessory:
            raise ValueError(f"Accessory {inspection_create.accessory_id} not found")

        # Calculate color period from inspection date
        color_period = SiteInspection.get_color_period(inspection_create.inspection_date)

        # Calculate next inspection date (2 months later)
        next_inspection = SiteInspection.calculate_next_inspection_date(
            inspection_create.inspection_date
        )

        # Determine status based on next inspection date
        status = (
            InspectionStatusEnum.VENCIDA
            if next_inspection < datetime.now(timezone.utc)
            else InspectionStatusEnum.VIGENTE
        )

        # Create inspection record
        inspection = SiteInspection(
            accessory_id=inspection_create.accessory_id,
            inspection_date=inspection_create.inspection_date,
            final_criterion=inspection_create.final_criterion,
            inspector_name=inspection_create.inspector_name,
            company=inspection_create.company,
            color_period=color_period,
            next_inspection_date=next_inspection,
            status=status,
            photo_urls=inspection_create.photo_urls,
            project_name=accessory.project.name if accessory.project else "Unknown",
            equipment_status=accessory.status.value,
        )

        db.add(inspection)
        await db.commit()
        await db.refresh(inspection)

        logger.info(
            f"Created site inspection for accessory {accessory.code_internal} "
            f"in period {color_period}"
        )
        return inspection

    @staticmethod
    async def update_inspection(
        db: AsyncSession,
        inspection_id: UUID,
        inspection_update: SiteInspectionUpdate,
    ) -> Optional[SiteInspection]:
        """
        Update a site inspection record.

        Args:
            db: Database session
            inspection_id: Inspection ID
            inspection_update: Inspection update schema

        Returns:
            Updated inspection object or None if not found
        """
        inspection = await SiteInspectionService.get_inspection_by_id(
            db, inspection_id
        )
        if not inspection:
            return None

        # Update fields if provided
        if inspection_update.final_criterion is not None:
            inspection.final_criterion = inspection_update.final_criterion
        if inspection_update.inspector_name is not None:
            inspection.inspector_name = inspection_update.inspector_name
        if inspection_update.company is not None:
            inspection.company = inspection_update.company
        if inspection_update.photo_urls is not None:
            inspection.photo_urls = inspection_update.photo_urls

        inspection.updated_at = datetime.now(timezone.utc)
        inspection.version += 1

        db.add(inspection)
        await db.commit()
        await db.refresh(inspection)

        logger.info(f"Updated site inspection {inspection_id}")
        return inspection

    @staticmethod
    async def add_photo(
        db: AsyncSession,
        inspection_id: UUID,
        photo_url: str,
    ) -> Optional[SiteInspection]:
        """
        Add a photo to a site inspection (appends to array).

        Args:
            db: Database session
            inspection_id: Inspection ID
            photo_url: URL/path to photo

        Returns:
            Updated inspection object or None if not found
        """
        inspection = await SiteInspectionService.get_inspection_by_id(
            db, inspection_id
        )
        if not inspection:
            return None

        # Initialize or append to photo array
        if inspection.photo_urls is None:
            inspection.photo_urls = [photo_url]
        else:
            inspection.photo_urls.append(photo_url)

        inspection.updated_at = datetime.now(timezone.utc)
        db.add(inspection)
        await db.commit()
        await db.refresh(inspection)

        logger.info(f"Added photo to site inspection {inspection_id}")
        return inspection

    @staticmethod
    async def get_latest_inspection(
        db: AsyncSession,
        accessory_id: UUID,
    ) -> Optional[SiteInspection]:
        """
        Get the latest site inspection for an accessory.

        Args:
            db: Database session
            accessory_id: Accessory ID

        Returns:
            Latest inspection object or None
        """
        stmt = (
            select(SiteInspection)
            .where(
                and_(
                    SiteInspection.accessory_id == accessory_id,
                    SiteInspection.deleted_at.is_(None),
                )
            )
            .order_by(SiteInspection.inspection_date.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_inspections_by_period(
        db: AsyncSession,
        color_period: ColorPeriodEnum,
    ) -> List[SiteInspection]:
        """
        Get all inspections for a specific color period.

        Args:
            db: Database session
            color_period: Color period enum

        Returns:
            List of inspections in that period
        """
        stmt = select(SiteInspection).where(
            and_(
                SiteInspection.color_period == color_period,
                SiteInspection.deleted_at.is_(None),
            )
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_expired_inspections(
        db: AsyncSession,
    ) -> List[SiteInspection]:
        """
        Get all expired site inspections.

        Args:
            db: Database session

        Returns:
            List of expired inspections
        """
        stmt = select(SiteInspection).where(
            and_(
                SiteInspection.status == InspectionStatusEnum.VENCIDA,
                SiteInspection.deleted_at.is_(None),
            )
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def soft_delete_inspection(db: AsyncSession, inspection_id: UUID) -> bool:
        """
        Soft delete an inspection record.

        Args:
            db: Database session
            inspection_id: Inspection ID

        Returns:
            True if successful, False if not found
        """
        inspection = await SiteInspectionService.get_inspection_by_id(
            db, inspection_id
        )
        if not inspection:
            return False

        inspection.deleted_at = datetime.now(timezone.utc)
        db.add(inspection)
        await db.commit()

        logger.info(f"Soft deleted site inspection {inspection_id}")
        return True
