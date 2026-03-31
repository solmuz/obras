from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class ProjectStatusEnum(str, Enum):
    """Project status enumeration."""
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"


# Association table for Project-User many-to-many relationship
project_users = Table(
    'project_users',
    Base.metadata,
    Column('project_id', UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('fecha_asignacion', DateTime(timezone=True), nullable=False, default=_utcnow),
    Column('fecha_remocion', DateTime(timezone=True), nullable=True),
)


class Project(Base):
    """Project model - central entity that groups accessories and employees."""
    
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    status = Column(SQLEnum(ProjectStatusEnum), nullable=False, default=ProjectStatusEnum.ACTIVO)
    start_date = Column(DateTime(timezone=True), nullable=False)
    
    # Foreign key for creator
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    employees = relationship(
        "User",
        secondary=project_users,
        backref="projects",
        lazy="selectin",
    )
    accessories = relationship(
        "Accessory",
        back_populates="project",
        lazy="selectin",
    )

    @property
    def employee_count(self) -> int:
        """Get the count of employees assigned to this project."""
        return len(self.employees) if self.employees else 0

    @property
    def accessory_count(self) -> int:
        """Get the count of accessories in this project."""
        return len(self.accessories) if self.accessories else 0

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"
