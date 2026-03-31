from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid

from app.db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class AuditActionEnum(str, Enum):
    """Audit trail action types."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class AuditLog(Base):
    """Audit trail model - append-only, immutable record of all system operations."""
    
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Who performed the action
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # What entity was affected
    entity_type = Column(String(50), nullable=False, index=True)  # e.g., "accessory", "project", "user"
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # ID of affected entity
    
    # What action was performed
    action = Column(SQLEnum(AuditActionEnum), nullable=False, index=True)
    
    # Details of the change
    old_values = Column(JSON, nullable=True)  # Previous state (null for CREATE)
    new_values = Column(JSON, nullable=True)  # New state (null for DELETE)
    change_description = Column(Text, nullable=True)  # Human-readable summary
    
    # When it happened (UTC)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, index=True)
    
    # Relationships
    user = relationship("User", lazy="selectin")

    def __repr__(self) -> str:
        return f"<AuditLog(user_id={self.user_id}, entity={self.entity_type}, action={self.action})>"
