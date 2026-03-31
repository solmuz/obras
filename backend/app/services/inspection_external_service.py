"""External inspection service - MOD-05 certification records."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta, timezone
import logging

from app.models.inspection_external import (
    ExternalInspection,
    ExternalInspectionCompanyEnum,
    InspectionStatusEnum,
)
from app.models.accessory import Accessory
from app.schemas.inspection import (
    ExternalInspectionCreate,
    ExternalInspectionUpdate,
)

logger = logging.getLogger(__name__)


class ExternalInspectionService:
    """Service for external (certified) inspections - MOD-05."""

    @staticmethod
    async def get_inspection_by_id(
        db: AsyncSession,
        inspection_id: UUID,
    ) -> Optional[ExternalInspection]:
        """
        Get external inspection by ID (active only).

        Args:
            db: Database session
            inspection_id: Inspection ID

        Returns:
            Inspection object or None if not found
        """
        stmt = select(ExternalInspection).where(
            and_(
                ExternalInspection.id == inspection_id,
                ExternalInspection.deleted_at.is_(None)
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
        company: Optional[ExternalInspectionCompanyEnum] = None,
    ) -> tuple[List[ExternalInspection], int]:
        """
        List external inspections with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Max records to return
            accessory_id: Filter by accessory (optional)
            status: Filter by status (optional)
            company: Filter by company (optional)

        Returns:
            Tuple of (list of inspections, total count)
        """
        # Build filter conditions
        conditions = [ExternalInspection.deleted_at.is_(None)]
        
        if accessory_id is not None:
            conditions.append(ExternalInspection.accessory_id == accessory_id)
        if status is not None:
            conditions.append(ExternalInspection.status == status)
        if company is not None:
            conditions.append(ExternalInspection.company == company)

        # Count query
        count_result = await db.execute(
            select(func.count()).select_from(ExternalInspection).where(and_(*conditions))
        )
        total_count = count_result.scalar() or 0

        # Data query
        stmt = (
            select(ExternalInspection)
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
        inspection_create: ExternalInspectionCreate,
    ) -> ExternalInspection:
        """
        Create a new external inspection record.

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

        # Calculate next inspection date (6 months later)
        next_inspection = ExternalInspection.calculate_next_inspection_date(
            inspection_create.inspection_date
        )

        # Determine status based on next inspection date
        status = (
            InspectionStatusEnum.VENCIDA
            if next_inspection < datetime.now(timezone.utc)
            else InspectionStatusEnum.VIGENTE
        )

        # Create inspection record
        inspection = ExternalInspection(
            accessory_id=inspection_create.accessory_id,
            inspection_date=inspection_create.inspection_date,
            company=inspection_create.company,
            company_responsible=inspection_create.company_responsible,
            final_criterion=inspection_create.final_criterion,
            next_inspection_date=next_inspection,
            status=status,
            certificate_pdf=inspection_create.certificate_pdf,
            certificate_number=inspection_create.certificate_number,
            project_name=accessory.project.name if accessory.project else "Unknown",
            equipment_status=accessory.status.value,
        )

        db.add(inspection)
        await db.commit()
        await db.refresh(inspection)

        logger.info(
            f"Created external inspection for accessory {accessory.code_internal}"
        )
        return inspection

    @staticmethod
    async def update_inspection(
        db: AsyncSession,
        inspection_id: UUID,
        inspection_update: ExternalInspectionUpdate,
    ) -> Optional[ExternalInspection]:
        """
        Update an external inspection record.

        Args:
            db: Database session
            inspection_id: Inspection ID
            inspection_update: Inspection update schema

        Returns:
            Updated inspection object or None if not found
        """
        inspection = await ExternalInspectionService.get_inspection_by_id(
            db, inspection_id
        )
        if not inspection:
            return None

        # Update fields if provided
        if inspection_update.company is not None:
            inspection.company = inspection_update.company
        if inspection_update.company_responsible is not None:
            inspection.company_responsible = inspection_update.company_responsible
        if inspection_update.final_criterion is not None:
            inspection.final_criterion = inspection_update.final_criterion
        if inspection_update.certificate_number is not None:
            inspection.certificate_number = inspection_update.certificate_number

        inspection.updated_at = datetime.now(timezone.utc)
        inspection.version += 1

        db.add(inspection)
        await db.commit()
        await db.refresh(inspection)

        logger.info(f"Updated external inspection {inspection_id}")
        return inspection

    @staticmethod
    async def get_latest_inspection(
        db: AsyncSession,
        accessory_id: UUID,
    ) -> Optional[ExternalInspection]:
        """
        Get the latest external inspection for an accessory.

        Args:
            db: Database session
            accessory_id: Accessory ID

        Returns:
            Latest inspection object or None
        """
        stmt = (
            select(ExternalInspection)
            .where(
                and_(
                    ExternalInspection.accessory_id == accessory_id,
                    ExternalInspection.deleted_at.is_(None),
                )
            )
            .order_by(ExternalInspection.inspection_date.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_expired_inspections(
        db: AsyncSession,
    ) -> List[ExternalInspection]:
        """
        Get all expired external inspections.

        Args:
            db: Database session

        Returns:
            List of expired inspections
        """
        stmt = select(ExternalInspection).where(
            and_(
                ExternalInspection.status == InspectionStatusEnum.VENCIDA,
                ExternalInspection.deleted_at.is_(None),
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
        inspection = await ExternalInspectionService.get_inspection_by_id(
            db, inspection_id
        )
        if not inspection:
            return False

        inspection.deleted_at = datetime.now(timezone.utc)
        db.add(inspection)
        await db.commit()

        logger.info(f"Soft deleted external inspection {inspection_id}")
        return True
