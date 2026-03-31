from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

from app.db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class DecommissionRecord(Base):
    """Decommission record (Acta de Baja) model - MOD-07."""
    
    __tablename__ = "decommission_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    accessory_id = Column(UUID(as_uuid=True), ForeignKey('accessories.id', ondelete='CASCADE'), nullable=False, index=True, unique=True)
    
    # Decommission data
    decommission_date = Column(DateTime(timezone=True), nullable=False)
    reason = Column(Text, nullable=False)  # Detailed reason for decommission
    responsible_name = Column(String(255), nullable=False)  # Person responsible for decommissioning
    
    # Photo storage (multiple photos documenting the decommissioned equipment)
    photo_urls = Column(ARRAY(String(500), dimensions=1), nullable=True)  # Array of photo paths
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    accessory = relationship("Accessory", back_populates="decommission_records", lazy="selectin")

    def __repr__(self) -> str:
        return f"<DecommissionRecord(accessory_id={self.accessory_id}, date={self.decommission_date})>"
