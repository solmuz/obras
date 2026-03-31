from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.models.user import User, RoleEnum
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_jwt_token,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication and JWT token management."""

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str,
    ) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            db: Database session
            email: User email
            password: Plain text password

        Returns:
            User object if authentication succeeds, None otherwise
        """
        stmt = select(User).where(User.email == email).where(User.deleted_at.is_(None))
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    def create_tokens(user: User) -> Dict[str, Any]:
        """
        Create access and refresh tokens for a user.

        Args:
            user: User object

        Returns:
            Dictionary containing tokens and expiration info
        """
        # Create JWT payload
        access_payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "type": "access",
        }

        refresh_payload = {
            "sub": str(user.id),
            "email": user.email,
            "type": "refresh",
        }

        access_token = create_access_token(access_payload)
        refresh_token = create_refresh_token(refresh_payload)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # In seconds
        }

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Token payload if valid, None otherwise
        """
        return decode_jwt_token(token)

    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a new access token from a valid refresh token.

        Args:
            db: Database session
            refresh_token: Refresh token string

        Returns:
            Dictionary with new access token, or None if refresh token is invalid
        """
        payload = decode_jwt_token(refresh_token)

        if not payload:
            return None

        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # Verify user still exists and is active
        stmt = select(User).where(User.id == user_id).where(User.deleted_at.is_(None))
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            return None

        # Create new token pair (rotate both access and refresh)
        access_payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "type": "access",
        }
        refresh_payload = {
            "sub": str(user.id),
            "email": user.email,
            "type": "refresh",
        }
        access_token = create_access_token(access_payload)
        new_refresh_token = create_refresh_token(refresh_payload)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password."""
        return hash_password(password)
