"""Audit logging service - Append-only audit trail."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timezone
import logging

from app.models.audit_log import AuditLog, AuditActionEnum
from app.models.user import User

logger = logging.getLogger(__name__)


def _convert_to_json_serializable(obj: Any) -> Any:
    """
    Recursively convert objects to JSON-serializable types.
    Converts UUID objects to strings.
    
    Args:
        obj: Object to convert (dict, list, or primitive)
        
    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: _convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj


class AuditService:
    """Service for audit trail logging - append-only, immutable records."""

    @staticmethod
    async def get_log_by_id(db: AsyncSession, log_id: UUID) -> Optional[AuditLog]:
        """
        Get audit log entry by ID.

        Args:
            db: Database session
            log_id: Log entry ID

        Returns:
            Audit log object or None if not found
        """
        stmt = select(AuditLog).where(AuditLog.id == log_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_logs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        action: Optional[AuditActionEnum] = None,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[List[AuditLog], int]:
        """
        List audit logs with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Max records to return
            entity_type: Filter by entity type (optional)
            entity_id: Filter by entity ID (optional)
            action: Filter by action type (optional)
            user_id: Filter by user who performed action (optional)
            start_date: Filter by date range start (optional)
            end_date: Filter by date range end (optional)

        Returns:
            Tuple of (list of logs, total count)
        """
        # Build filter conditions
        conditions = []
        
        if entity_type is not None:
            conditions.append(AuditLog.entity_type == entity_type)
        if entity_id is not None:
            conditions.append(AuditLog.entity_id == entity_id)
        if action is not None:
            conditions.append(AuditLog.action == action)
        if user_id is not None:
            conditions.append(AuditLog.user_id == user_id)
        if start_date is not None:
            conditions.append(AuditLog.created_at >= start_date)
        if end_date is not None:
            conditions.append(AuditLog.created_at <= end_date)

        # Count query
        if conditions:
            count_result = await db.execute(
                select(func.count()).select_from(AuditLog).where(and_(*conditions))
            )
        else:
            count_result = await db.execute(
                select(func.count()).select_from(AuditLog)
            )
        total_count = count_result.scalar() or 0

        # Data query (ordered by creation date descending)
        if conditions:
            stmt = (
                select(AuditLog)
                .where(and_(*conditions))
                .order_by(AuditLog.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
        else:
            stmt = (
                select(AuditLog)
                .order_by(AuditLog.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
        result = await db.execute(stmt)
        logs = result.scalars().all()

        return logs, total_count

    @staticmethod
    async def log_create(
        db: AsyncSession,
        entity_type: str,
        entity_id: UUID,
        new_values: Dict[str, Any],
        user_id: Optional[UUID] = None,
        description: Optional[str] = None,
    ) -> AuditLog:
        """
        Log a CREATE action.

        Args:
            db: Database session
            entity_type: Type of entity created (e.g., 'user', 'project', 'accessory')
            entity_id: ID of created entity
            new_values: New values of the entity
            user_id: ID of user performing the action (optional)
            description: Human-readable description (optional)

        Returns:
            Created audit log entry
        """
        # Convert UUIDs and other non-serializable objects to JSON-safe types
        serializable_new_values = _convert_to_json_serializable(new_values)
        
        log = AuditLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=AuditActionEnum.CREATE,
            old_values=None,
            new_values=serializable_new_values,
            change_description=description or f"Created {entity_type}",
        )

        db.add(log)
        await db.commit()
        await db.refresh(log)

        logger.info(
            f"Audit: CREATE {entity_type} {entity_id} by user {user_id}"
        )
        return log

    @staticmethod
    async def log_update(
        db: AsyncSession,
        entity_type: str,
        entity_id: UUID,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        user_id: Optional[UUID] = None,
        description: Optional[str] = None,
    ) -> AuditLog:
        """
        Log an UPDATE action.

        Args:
            db: Database session
            entity_type: Type of entity updated
            entity_id: ID of updated entity
            old_values: Previous values
            new_values: New values
            user_id: ID of user performing the action (optional)
            description: Human-readable description (optional)

        Returns:
            Created audit log entry
        """
        # Convert UUIDs and other non-serializable objects to JSON-safe types
        serializable_old_values = _convert_to_json_serializable(old_values)
        serializable_new_values = _convert_to_json_serializable(new_values)
        
        log = AuditLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=AuditActionEnum.UPDATE,
            old_values=serializable_old_values,
            new_values=serializable_new_values,
            change_description=description or f"Updated {entity_type}",
        )

        db.add(log)
        await db.commit()
        await db.refresh(log)

        logger.info(
            f"Audit: UPDATE {entity_type} {entity_id} by user {user_id}"
        )
        return log

    @staticmethod
    async def log_delete(
        db: AsyncSession,
        entity_type: str,
        entity_id: UUID,
        old_values: Dict[str, Any],
        user_id: Optional[UUID] = None,
        description: Optional[str] = None,
    ) -> AuditLog:
        """
        Log a DELETE action (soft or hard).

        Args:
            db: Database session
            entity_type: Type of entity deleted
            entity_id: ID of deleted entity
            old_values: Previous values (before deletion)
            user_id: ID of user performing the action (optional)
            description: Human-readable description (optional)

        Returns:
            Created audit log entry
        """
        # Convert UUIDs and other non-serializable objects to JSON-safe types
        serializable_old_values = _convert_to_json_serializable(old_values)
        
        log = AuditLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=AuditActionEnum.DELETE,
            old_values=serializable_old_values,
            new_values=None,
            change_description=description or f"Deleted {entity_type}",
        )

        db.add(log)
        await db.commit()
        await db.refresh(log)

        logger.info(
            f"Audit: DELETE {entity_type} {entity_id} by user {user_id}"
        )
        return log

    @staticmethod
    async def get_entity_history(
        db: AsyncSession,
        entity_type: str,
        entity_id: UUID,
    ) -> List[AuditLog]:
        """
        Get complete audit history for a specific entity.

        Args:
            db: Database session
            entity_type: Type of entity
            entity_id: ID of entity

        Returns:
            List of audit log entries for that entity, ordered by date ascending
        """
        stmt = (
            select(AuditLog)
            .where(
                and_(
                    AuditLog.entity_type == entity_type,
                    AuditLog.entity_id == entity_id,
                )
            )
            .order_by(AuditLog.created_at.asc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_user_actions(
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[AuditLog], int]:
        """
        Get all actions performed by a specific user.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Max records to return

        Returns:
            Tuple of (list of logs, total count)
        """
        # Count query
        count_result = await db.execute(
            select(func.count()).select_from(AuditLog).where(
                AuditLog.user_id == user_id
            )
        )
        total_count = count_result.scalar() or 0

        # Data query
        stmt = (
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        logs = result.scalars().all()

        return logs, total_count

    @staticmethod
    async def get_recent_activity(
        db: AsyncSession,
        hours: int = 24,
    ) -> List[AuditLog]:
        """
        Get recent audit activity (last N hours).

        Args:
            db: Database session
            hours: Number of hours to look back

        Returns:
            List of recent audit logs
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        stmt = (
            select(AuditLog)
            .where(AuditLog.created_at >= cutoff_time)
            .order_by(AuditLog.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()
