"""Decommission record service - MOD-07 equipment retirement."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timezone
import logging

from app.models.decommission import DecommissionRecord
from app.models.accessory import Accessory
from app.schemas.decommission import (
    DecommissionCreate,
    DecommissionUpdate,
)

logger = logging.getLogger(__name__)


class DecommissionService:
    """Service for decommission records (Acta de Baja) - MOD-07."""

    @staticmethod
    async def get_record_by_id(
        db: AsyncSession,
        record_id: UUID,
    ) -> Optional[DecommissionRecord]:
        """
        Get decommission record by ID (active only).

        Args:
            db: Database session
            record_id: Record ID

        Returns:
            Record object or None if not found
        """
        stmt = select(DecommissionRecord).where(
            and_(
                DecommissionRecord.id == record_id,
                DecommissionRecord.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_record_by_accessory(
        db: AsyncSession,
        accessory_id: UUID,
    ) -> Optional[DecommissionRecord]:
        """
        Get decommission record for an accessory (each accessory can be decommissioned once).

        Args:
            db: Database session
            accessory_id: Accessory ID

        Returns:
            Record object or None if not found
        """
        stmt = select(DecommissionRecord).where(
            and_(
                DecommissionRecord.accessory_id == accessory_id,
                DecommissionRecord.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_records(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[DecommissionRecord], int]:
        """
        List decommission records.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Max records to return

        Returns:
            Tuple of (list of records, total count)
        """
        # Count query
        count_result = await db.execute(
            select(func.count()).select_from(DecommissionRecord).where(
                DecommissionRecord.deleted_at.is_(None)
            )
        )
        total_count = count_result.scalar() or 0

        # Data query
        stmt = (
            select(DecommissionRecord)
            .where(DecommissionRecord.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        records = result.scalars().all()

        return records, total_count

    @staticmethod
    async def create_record(
        db: AsyncSession,
        record_create: DecommissionCreate,
    ) -> DecommissionRecord:
        """
        Create a new decommission record.

        Args:
            db: Database session
            record_create: Record creation schema

        Returns:
            Created record object

        Raises:
            ValueError: If accessory not found or already decommissioned
        """
        # Verify accessory exists and is active
        accessory_stmt = select(Accessory).where(
            and_(
                Accessory.id == record_create.accessory_id,
                Accessory.deleted_at.is_(None)
            )
        )
        accessory_result = await db.execute(accessory_stmt)
        accessory = accessory_result.scalar_one_or_none()
        if not accessory:
            raise ValueError(f"Accessory {record_create.accessory_id} not found")

        # Check if already decommissioned
        existing = await DecommissionService.get_record_by_accessory(
            db, record_create.accessory_id
        )
        if existing:
            raise ValueError(f"Accessory {record_create.accessory_id} already has a decommission record")

        # Create decommission record
        record = DecommissionRecord(
            accessory_id=record_create.accessory_id,
            decommission_date=record_create.decommission_date,
            reason=record_create.reason,
            responsible_name=record_create.responsible_name,
            photo_urls=record_create.photo_urls,
        )

        db.add(record)
        await db.commit()
        await db.refresh(record)

        logger.info(f"Created decommission record for accessory {accessory.code_internal}")
        return record

    @staticmethod
    async def update_record(
        db: AsyncSession,
        record_id: UUID,
        record_update: DecommissionUpdate,
    ) -> Optional[DecommissionRecord]:
        """
        Update a decommission record.

        Args:
            db: Database session
            record_id: Record ID
            record_update: Record update schema

        Returns:
            Updated record object or None if not found
        """
        record = await DecommissionService.get_record_by_id(db, record_id)
        if not record:
            return None

        # Update fields if provided
        if record_update.reason is not None:
            record.reason = record_update.reason
        if record_update.responsible_name is not None:
            record.responsible_name = record_update.responsible_name
        if record_update.photo_urls is not None:
            record.photo_urls = record_update.photo_urls

        record.updated_at = datetime.now(timezone.utc)
        db.add(record)
        await db.commit()
        await db.refresh(record)

        logger.info(f"Updated decommission record {record_id}")
        return record

    @staticmethod
    async def add_photo(
        db: AsyncSession,
        record_id: UUID,
        photo_url: str,
    ) -> Optional[DecommissionRecord]:
        """
        Add a photo to a decommission record (appends to array).

        Args:
            db: Database session
            record_id: Record ID
            photo_url: URL/path to photo

        Returns:
            Updated record object or None if not found
        """
        record = await DecommissionService.get_record_by_id(db, record_id)
        if not record:
            return None

        # Initialize or append to photo array
        if record.photo_urls is None:
            record.photo_urls = [photo_url]
        else:
            record.photo_urls.append(photo_url)

        record.updated_at = datetime.now(timezone.utc)
        db.add(record)
        await db.commit()
        await db.refresh(record)

        logger.info(f"Added photo to decommission record {record_id}")
        return record

    @staticmethod
    async def soft_delete_record(db: AsyncSession, record_id: UUID) -> bool:
        """
        Soft delete a decommission record.

        Args:
            db: Database session
            record_id: Record ID

        Returns:
            True if successful, False if not found
        """
        record = await DecommissionService.get_record_by_id(db, record_id)
        if not record:
            return False

        record.deleted_at = datetime.now(timezone.utc)
        db.add(record)
        await db.commit()

        logger.info(f"Soft deleted decommission record {record_id}")
        return True

    @staticmethod
    async def restore_record(
        db: AsyncSession,
        record_id: UUID,
    ) -> Optional[DecommissionRecord]:
        """
        Restore a soft-deleted decommission record.

        Args:
            db: Database session
            record_id: Record ID

        Returns:
            Restored record or None if not found
        """
        stmt = select(DecommissionRecord).where(DecommissionRecord.id == record_id)
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        record.deleted_at = None
        db.add(record)
        await db.commit()
        await db.refresh(record)

        logger.info(f"Restored decommission record {record_id}")
        return record
