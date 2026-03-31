"""User management service - CRUD operations for users."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging

from app.models.user import User, RoleEnum
from app.core.security import hash_password, verify_password
from app.schemas.user import UserCreate, UserUpdate, UserOut

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management and CRUD operations."""

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """
        Get user by ID (including soft-deleted).

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object or None if not found
        """
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id_active(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """
        Get active user by ID (excludes soft-deleted).

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Active user object or None if not found
        """
        stmt = select(User).where(
            and_(
                User.id == user_id,
                User.deleted_at.is_(None),
                User.is_active.is_(True)
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email (active users only).

        Args:
            db: Database session
            email: User email

        Returns:
            User object or None if not found
        """
        stmt = select(User).where(
            and_(
                User.email == email,
                User.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        role: Optional[RoleEnum] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[User], int]:
        """
        List users with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Max records to return
            role: Filter by role (optional)
            is_active: Filter by active status (optional)

        Returns:
            Tuple of (list of users, total count)
        """
        # Build filter conditions
        conditions = [User.deleted_at.is_(None)]
        
        if role is not None:
            conditions.append(User.role == role)
        if is_active is not None:
            conditions.append(User.is_active == is_active)

        # Count query
        count_stmt = select(User).where(and_(*conditions))
        count_result = await db.execute(select(User).where(and_(*conditions)))
        total_count = len(count_result.scalars().all())

        # Data query
        stmt = select(User).where(and_(*conditions)).offset(skip).limit(limit)
        result = await db.execute(stmt)
        users = result.scalars().all()

        return users, total_count

    @staticmethod
    async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
        """
        Create a new user.

        Args:
            db: Database session
            user_create: User creation schema

        Returns:
            Created user object
        """
        # Hash password
        hashed_password = hash_password(user_create.password)

        # Create user
        user = User(
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=hashed_password,
            role=user_create.role,
            is_active=True,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(f"Created user: {user.email} with role {user.role}")
        return user

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: UUID,
        user_update: UserUpdate,
    ) -> Optional[User]:
        """
        Update user information.

        Args:
            db: Database session
            user_id: User ID
            user_update: User update schema

        Returns:
            Updated user object or None if not found
        """
        user = await UserService.get_user_by_id_active(db, user_id)
        if not user:
            return None

        # Update fields if provided
        if user_update.full_name is not None:
            user.full_name = user_update.full_name
        if user_update.role is not None:
            user.role = user_update.role
        if user_update.is_active is not None:
            user.is_active = user_update.is_active

        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(f"Updated user: {user.email}")
        return user

    @staticmethod
    async def change_password(
        db: AsyncSession,
        user_id: UUID,
        old_password: str,
        new_password: str,
    ) -> bool:
        """
        Change user password.

        Args:
            db: Database session
            user_id: User ID
            old_password: Current password (plain text)
            new_password: New password (plain text)

        Returns:
            True if successful, False otherwise
        """
        user = await UserService.get_user_by_id_active(db, user_id)
        if not user:
            return False

        # Verify old password
        if not verify_password(old_password, user.hashed_password):
            return False

        # Set new password
        user.hashed_password = hash_password(new_password)
        db.add(user)
        await db.commit()

        logger.info(f"User {user.email} changed password")
        return True

    @staticmethod
    async def soft_delete_user(db: AsyncSession, user_id: UUID) -> bool:
        """
        Soft delete a user (mark as deleted, preserve data).

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if successful, False if user not found
        """
        from datetime import datetime, timezone
        
        user = await UserService.get_user_by_id_active(db, user_id)
        if not user:
            return False

        user.deleted_at = datetime.now(timezone.utc)
        user.is_active = False
        db.add(user)
        await db.commit()

        logger.info(f"Soft deleted user: {user.email}")
        return True

    @staticmethod
    async def hard_delete_user(db: AsyncSession, user_id: UUID) -> bool:
        """
        Hard delete a user (permanent deletion from database).

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if successful, False if user not found
        """
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return False

        await db.delete(user)
        await db.commit()

        logger.info(f"Hard deleted user: {user.email}")
        return True

    @staticmethod
    async def restore_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """
        Restore a soft-deleted user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Restored user or None if not found
        """
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        user.deleted_at = None
        user.is_active = True
        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(f"Restored user: {user.email}")
        return user
