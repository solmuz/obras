"""Report and semáforo service - Equipment status dashboard and aggregations."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta, timezone
import logging

from app.models.accessory import Accessory, UsageStatusEnum, ElementTypeEnum, BrandEnum
from app.models.project import Project
from app.models.inspection_external import ExternalInspection, InspectionStatusEnum as ExtInspectionStatus
from app.models.inspection_site import SiteInspection, ColorPeriodEnum, InspectionStatusEnum as SiteInspectionStatus
from app.models.decommission import DecommissionRecord

logger = logging.getLogger(__name__)


class ReportService:
    """Service for equipment status reporting and semáforo calculations."""

    # Semáforo status definitions
    VERDE = "VERDE"  # Green: All inspections current
    AMARILLO = "AMARILLO"  # Yellow: At least one inspection expiring soon
    ROJO = "ROJO"  # Red: At least one inspection expired

    @staticmethod
    async def calculate_accessory_semaforo(
        db: AsyncSession,
        accessory_id: UUID,
    ) -> str:
        """
        Calculate semáforo status for a single accessory based on inspections.

        Semáforo logic:
        - RED: Any external or site inspection is VENCIDA (expired)
        - YELLOW: No RED conditions, but inspection expires within 30 days
        - GREEN: All inspections current and not expiring soon

        Args:
            db: Database session
            accessory_id: Accessory ID

        Returns:
            Status string: "VERDE", "AMARILLO", or "ROJO"
        """
        # Get all inspections for this accessory
        external_stmt = select(ExternalInspection).where(
            and_(
                ExternalInspection.accessory_id == accessory_id,
                ExternalInspection.deleted_at.is_(None),
            )
        )
        external_result = await db.execute(external_stmt)
        external_inspections = external_result.scalars().all()

        site_stmt = select(SiteInspection).where(
            and_(
                SiteInspection.accessory_id == accessory_id,
                SiteInspection.deleted_at.is_(None),
            )
        )
        site_result = await db.execute(site_stmt)
        site_inspections = site_result.scalars().all()

        # Check if decommissioned
        decommission_stmt = select(DecommissionRecord).where(
            and_(
                DecommissionRecord.accessory_id == accessory_id,
                DecommissionRecord.deleted_at.is_(None),
            )
        )
        decommission_result = await db.execute(decommission_stmt)
        if decommission_result.scalar_one_or_none():
            return "DECOMMISSIONED"

        # Check for RED conditions (expired)
        now = datetime.now(timezone.utc)
        
        for inspection in external_inspections:
            if inspection.status == ExtInspectionStatus.VENCIDA:
                return ReportService.ROJO

        for inspection in site_inspections:
            if inspection.status == SiteInspectionStatus.VENCIDA:
                return ReportService.ROJO

        # Check for YELLOW conditions (expiring soon)
        thirty_days = now + timedelta(days=30)

        for inspection in external_inspections:
            if inspection.next_inspection_date <= thirty_days:
                return ReportService.AMARILLO

        for inspection in site_inspections:
            if inspection.next_inspection_date <= thirty_days:
                return ReportService.AMARILLO

        # Green condition (all current)
        return ReportService.VERDE

    @staticmethod
    async def get_project_semaforo_summary(
        db: AsyncSession,
        project_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get semáforo summary for a project.

        Returns counts of equipment by status and aggregated status.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            Dictionary with counts and overall status
        """
        # Get all accessories in project
        accessories_stmt = select(Accessory).where(
            and_(
                Accessory.project_id == project_id,
                Accessory.deleted_at.is_(None)
            )
        )
        accessories_result = await db.execute(accessories_stmt)
        accessories = accessories_result.scalars().all()

        # Calculate status for each
        verde_count = 0
        amarillo_count = 0
        rojo_count = 0
        decommissioned_count = 0

        for accessory in accessories:
            status = await ReportService.calculate_accessory_semaforo(db, accessory.id)
            
            if status == ReportService.VERDE:
                verde_count += 1
            elif status == ReportService.AMARILLO:
                amarillo_count += 1
            elif status == ReportService.ROJO:
                rojo_count += 1
            elif status == "DECOMMISSIONED":
                decommissioned_count += 1

        # Determine overall status
        if rojo_count > 0:
            overall_status = ReportService.ROJO
        elif amarillo_count > 0:
            overall_status = ReportService.AMARILLO
        else:
            overall_status = ReportService.VERDE

        return {
            "project_id": str(project_id),
            "total_equipment": len(accessories),
            "verde_count": verde_count,
            "amarillo_count": amarillo_count,
            "rojo_count": rojo_count,
            "decommissioned_count": decommissioned_count,
            "overall_status": overall_status,
        }

    @staticmethod
    async def get_global_semaforo_summary(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        semaforo_status: Optional[str] = None,
        project_id: Optional[UUID] = None,
        element_type: Optional[ElementTypeEnum] = None,
        brand: Optional[BrandEnum] = None,
        usage_status: Optional[UsageStatusEnum] = None,
    ) -> List[Accessory]:
        """
        Get accessories with their semáforo status, filtered and paginated.

        Returns a list of Accessory objects with a `semaforo_status` attribute set.
        """
        conditions = [Accessory.deleted_at.is_(None)]
        if project_id:
            conditions.append(Accessory.project_id == project_id)
        if element_type:
            conditions.append(Accessory.element_type == element_type)
        if brand:
            conditions.append(Accessory.brand == brand)
        if usage_status:
            conditions.append(Accessory.status == usage_status)

        accessories_stmt = select(Accessory).where(and_(*conditions))
        accessories_result = await db.execute(accessories_stmt)
        accessories = accessories_result.scalars().all()

        # Compute semáforo for each
        result = []
        for accessory in accessories:
            status = await ReportService.calculate_accessory_semaforo(db, accessory.id)
            if status == "DECOMMISSIONED":
                status = ReportService.ROJO
            if semaforo_status and status != semaforo_status:
                continue
            accessory.semaforo_status = status
            result.append(accessory)

        # Apply pagination after filtering
        return result[skip : skip + limit]

    @staticmethod
    async def get_expiring_inspections(
        db: AsyncSession,
        days: int = 30,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all inspections expiring within N days.

        Args:
            db: Database session
            days: Number of days to look ahead

        Returns:
            Dictionary with lists of expiring external and site inspections
        """
        cutoff_date = datetime.now(timezone.utc) + timedelta(days=days)
        
        # Get expiring external inspections
        ext_stmt = select(ExternalInspection).where(
            and_(
                ExternalInspection.next_inspection_date <= cutoff_date,
                ExternalInspection.next_inspection_date > datetime.now(timezone.utc),
                ExternalInspection.status == ExtInspectionStatus.VIGENTE,
                ExternalInspection.deleted_at.is_(None),
            )
        ).order_by(ExternalInspection.next_inspection_date.asc())
        
        ext_result = await db.execute(ext_stmt)
        external_inspections = ext_result.scalars().all()

        # Get expiring site inspections
        site_stmt = select(SiteInspection).where(
            and_(
                SiteInspection.next_inspection_date <= cutoff_date,
                SiteInspection.next_inspection_date > datetime.now(timezone.utc),
                SiteInspection.status == SiteInspectionStatus.VIGENTE,
                SiteInspection.deleted_at.is_(None),
            )
        ).order_by(SiteInspection.next_inspection_date.asc())
        
        site_result = await db.execute(site_stmt)
        site_inspections = site_result.scalars().all()

        return {
            "expiring_external_inspections": [
                {
                    "id": str(insp.id),
                    "accessory_id": str(insp.accessory_id),
                    "next_inspection_date": insp.next_inspection_date.isoformat(),
                    "company": insp.company.value,
                    "days_until_expiry": (insp.next_inspection_date - datetime.now(timezone.utc)).days,
                }
                for insp in external_inspections
            ],
            "expiring_site_inspections": [
                {
                    "id": str(insp.id),
                    "accessory_id": str(insp.accessory_id),
                    "next_inspection_date": insp.next_inspection_date.isoformat(),
                    "color_period": insp.color_period.value,
                    "days_until_expiry": (insp.next_inspection_date - datetime.now(timezone.utc)).days,
                }
                for insp in site_inspections
            ],
        }

    @staticmethod
    async def get_project_statistics(
        db: AsyncSession,
        project_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a project.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            Dictionary with project statistics
        """
        # Get project
        project_stmt = select(Project).where(
            and_(
                Project.id == project_id,
                Project.deleted_at.is_(None)
            )
        )
        project_result = await db.execute(project_stmt)
        project = project_result.scalar_one_or_none()
        
        if not project:
            return None

        # Get accessories
        accessories_stmt = select(Accessory).where(
            and_(
                Accessory.project_id == project_id,
                Accessory.deleted_at.is_(None)
            )
        )
        accessories_result = await db.execute(accessories_stmt)
        accessories = accessories_result.scalars().all()

        # Count by status
        en_uso = sum(1 for a in accessories if a.status == UsageStatusEnum.EN_USO)
        en_stock = sum(1 for a in accessories if a.status == UsageStatusEnum.EN_STOCK)
        tag_rojo = sum(1 for a in accessories if a.status == UsageStatusEnum.TAG_ROJO)

        # Get semáforo summary
        semaforo = await ReportService.get_project_semaforo_summary(db, project_id)

        return {
            "project_id": str(project_id),
            "project_name": project.name,
            "status": project.status.value,
            "start_date": project.start_date.isoformat(),
            "equipment_statistics": {
                "total": len(accessories),
                "en_uso": en_uso,
                "en_stock": en_stock,
                "tag_rojo": tag_rojo,
            },
            "semaforo": semaforo,
        }

    @staticmethod
    async def get_equipment_by_semaforo(
        db: AsyncSession,
        status: str,
        project_id: Optional[UUID] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all equipment with a specific semáforo status.

        Args:
            db: Database session
            status: Status to filter by ("VERDE", "AMARILLO", "ROJO")
            project_id: Filter by project (optional)

        Returns:
            List of equipment with matching status
        """
        # Get all relevant accessories
        conditions = [Accessory.deleted_at.is_(None)]
        if project_id:
            conditions.append(Accessory.project_id == project_id)

        accessories_stmt = select(Accessory).where(and_(*conditions))
        accessories_result = await db.execute(accessories_stmt)
        accessories = accessories_result.scalars().all()

        matching_equipment = []
        
        for accessory in accessories:
            accessory_status = await ReportService.calculate_accessory_semaforo(
                db, accessory.id
            )
            
            if accessory_status == status:
                matching_equipment.append({
                    "id": str(accessory.id),
                    "code": accessory.code_internal,
                    "element_type": accessory.element_type.value,
                    "brand": accessory.brand.value,
                    "status": accessory.status.value,
                    "semaforo": status,
                })

        return matching_equipment
