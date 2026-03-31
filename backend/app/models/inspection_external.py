from datetime import datetime, timedelta, timezone
from enum import Enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class InspectionStatusEnum(str, Enum):
    """Inspection status - computed based on expiration date."""
    VIGENTE = "VIGENTE"
    VENCIDA = "VENCIDA"


class ExternalInspectionCompanyEnum(str, Enum):
    """Companies for external inspections."""
    GEO = "GEO"
    SBCIMAS = "SBCIMAS"
    PREFA = "PREFA"
    BESSAC = "BESSAC"


class ExternalInspection(Base):
    """External (certified) inspection model - MOD-05."""
    
    __tablename__ = "external_inspections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    accessory_id = Column(UUID(as_uuid=True), ForeignKey('accessories.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Inspection data
    inspection_date = Column(DateTime(timezone=True), nullable=False)
    company = Column(SQLEnum(ExternalInspectionCompanyEnum), nullable=False)
    company_responsible = Column(String(255), nullable=False)  # Certificating company name
    final_criterion = Column(String(255), nullable=False)  # Inspection result/conclusion
    
    # Auto-calculated fields
    next_inspection_date = Column(DateTime(timezone=True), nullable=False)  # inspection_date + 6 months
    status = Column(SQLEnum(InspectionStatusEnum), nullable=False, default=InspectionStatusEnum.VIGENTE)
    
    # File storage
    certificate_pdf = Column(String(500), nullable=False)  # Path to PDF certificate
    certificate_number = Column(String(100), nullable=True)  # May coincide with equipment code
    
    # Phase when recorded (denormalized for convenience)
    project_name = Column(String(255), nullable=False)  # Project where equipment belongs
    equipment_status = Column(String(50), nullable=False)  # EN_USO / EN_STOCK / TAG_ROJO snapshot
    
    # Tracking field for optimistic locking
    version = Column(Integer, nullable=False, default=1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    accessory = relationship("Accessory", back_populates="external_inspections", lazy="selectin")

    @staticmethod
    def calculate_next_inspection_date(inspection_date: datetime) -> datetime:
        """Calculate next external inspection date (6 months later)."""
        return inspection_date + timedelta(days=180)

    def __repr__(self) -> str:
        return f"<ExternalInspection(accessory_id={self.accessory_id}, date={self.inspection_date}, status={self.status})>"
