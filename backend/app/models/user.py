from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class RoleEnum(str, Enum):
    """User role enumeration."""
    ADMIN = "ADMIN"
    INGENIERO_HSE = "INGENIERO_HSE"
    CONSULTA = "CONSULTA"


class User(Base):
    """User model for authentication and role-based access control."""
    
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(RoleEnum), nullable=False, default=RoleEnum.CONSULTA)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
