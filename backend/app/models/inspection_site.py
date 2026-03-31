from datetime import datetime, timedelta, timezone
from enum import Enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

from app.db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class ColorPeriodEnum(str, Enum):
    """Bimonthly color-code inspection periods."""
    ENE_FEB = "ENE_FEB"
    MAR_ABR = "MAR_ABR"
    MAY_JUN = "MAY_JUN"
    JUL_AGO = "JUL_AGO"
    SEP_OCT = "SEP_OCT"
    NOV_DIC = "NOV_DIC"


class SiteInspectionResultEnum(str, Enum):
    """Result of on-site inspection."""
    BUEN_ESTADO = "BUEN_ESTADO"
    MAL_ESTADO = "MAL_ESTADO"
    OBSERVACIONES = "OBSERVACIONES"


class InspectionStatusEnum(str, Enum):
    """Inspection status - computed based on expiration date."""
    VIGENTE = "VIGENTE"
    VENCIDA = "VENCIDA"


class SiteInspectionCompanyEnum(str, Enum):
    """Companies for on-site inspections."""
    GEO = "GEO"
    SBCIMAS = "SBCIMAS"
    PREFA = "PREFA"
    BESSAC = "BESSAC"


class SiteInspection(Base):
    """On-site color-code inspection model - MOD-06."""
    
    __tablename__ = "site_inspections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    accessory_id = Column(UUID(as_uuid=True), ForeignKey('accessories.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Inspection data
    inspection_date = Column(DateTime(timezone=True), nullable=False)
    final_criterion = Column(SQLEnum(SiteInspectionResultEnum), nullable=False)
    inspector_name = Column(String(255), nullable=False)  # Person responsible
    company = Column(SQLEnum(SiteInspectionCompanyEnum), nullable=False)
    
    # Auto-calculated fields
    color_period = Column(SQLEnum(ColorPeriodEnum), nullable=False)  # Calculated from inspection_date
    next_inspection_date = Column(DateTime(timezone=True), nullable=False)  # inspection_date + 2 months
    status = Column(SQLEnum(InspectionStatusEnum), nullable=False, default=InspectionStatusEnum.VIGENTE)
    
    # Photo storage (multiple photos per inspection)
    photo_urls = Column(ARRAY(String(500), dimensions=1), nullable=True)  # Array of photo paths
    
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
    accessory = relationship("Accessory", back_populates="site_inspections", lazy="selectin")

    @staticmethod
    def get_color_period(inspection_date: datetime) -> ColorPeriodEnum:
        """Determine color period from inspection date."""
        month = inspection_date.month
        
        if month in (1, 2):
            return ColorPeriodEnum.ENE_FEB
        elif month in (3, 4):
            return ColorPeriodEnum.MAR_ABR
        elif month in (5, 6):
            return ColorPeriodEnum.MAY_JUN
        elif month in (7, 8):
            return ColorPeriodEnum.JUL_AGO
        elif month in (9, 10):
            return ColorPeriodEnum.SEP_OCT
        else:  # 11, 12
            return ColorPeriodEnum.NOV_DIC

    @staticmethod
    def calculate_next_inspection_date(inspection_date: datetime) -> datetime:
        """Calculate next site inspection date (2 months later)."""
        return inspection_date + timedelta(days=60)

    def __repr__(self) -> str:
        return f"<SiteInspection(accessory_id={self.accessory_id}, period={self.color_period}, status={self.status})>"
