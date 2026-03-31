from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class BrandEnum(str, Enum):
    """Equipment brand enumeration."""
    BRAND_1 = "BRAND_1"
    BRAND_2 = "BRAND_2"
    BRAND_3 = "BRAND_3"


class ElementTypeEnum(str, Enum):
    """Type of lifting accessory."""
    ESLINGAS = "ESLINGAS"
    GRILLETES = "GRILLETES"
    GANCHOS = "GANCHOS"
    OTROS = "OTROS"


class UsageStatusEnum(str, Enum):
    """Equipment usage status."""
    EN_USO = "EN_USO"
    EN_STOCK = "EN_STOCK"
    TAG_ROJO = "TAG_ROJO"


class Accessory(Base):
    """Accessory/Equipment model - hoja de vida with fixed and mutable fields."""
    
    __tablename__ = "accessories"

    # Fixed fields (immutable)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code_internal = Column(String(50), unique=True, nullable=False, index=True)
    element_type = Column(SQLEnum(ElementTypeEnum), nullable=False)
    brand = Column(SQLEnum(BrandEnum), nullable=False)
    serial = Column(String(255), nullable=False)
    material = Column(String(255), nullable=False)
    capacity_vertical = Column(String(100), nullable=True)  # "V: 2 TON"
    capacity_choker = Column(String(100), nullable=True)    # "C: 1.6 TON"
    capacity_basket = Column(String(100), nullable=True)    # "B: 3 TON"
    length_m = Column(Float, nullable=True)
    diameter_inches = Column(String(50), nullable=True)
    num_ramales = Column(Integer, nullable=True)  # Only for eslingas

    # Mutable fields
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    status = Column(SQLEnum(UsageStatusEnum), nullable=False, default=UsageStatusEnum.EN_USO)
    
    # Photo URLs (stored paths)
    photo_accessory = Column(String(500), nullable=True)
    photo_manufacturer_label = Column(String(500), nullable=True)
    photo_provider_marking = Column(String(500), nullable=True)
    
    # Tracking field for optimistic locking
    version = Column(Integer, nullable=False, default=1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    project = relationship("Project", back_populates="accessories", lazy="selectin")
    external_inspections = relationship(
        "ExternalInspection",
        back_populates="accessory",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    site_inspections = relationship(
        "SiteInspection",
        back_populates="accessory",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    decommission_records = relationship(
        "DecommissionRecord",
        back_populates="accessory",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Accessory(code={self.code_internal}, brand={self.brand}, status={self.status})>"
