"""
Equipment service - Business logic for equipment management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal

from app.models.equipment import (
    EquipmentMaster,
    EquipmentSpecification,
    EquipmentHistoryCard,
    EquipmentUtilization,
    EquipmentStatus,
)
from app.schemas.equipment import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentHistoryCreate,
    EquipmentUtilizationCreate,
)
from app.core.config import settings
import qrcode
from io import BytesIO
import base64


class EquipmentService:
    """Service for equipment management operations"""

    @staticmethod
    def generate_equipment_id(department: str, year: Optional[int] = None) -> str:
        """
        Generate unique equipment ID in format: EQP-DEPT-YYYY-XXX
        Note: In production, this should query DB for last sequence number
        """
        if year is None:
            year = datetime.now().year

        dept_code = department[:4].upper()
        # In production, query database for last sequence
        sequence = "001"  # This should be incremented based on existing records

        return f"{settings.EQUIPMENT_ID_PREFIX}-{dept_code}-{year}-{sequence}"

    @staticmethod
    async def get_next_sequence_number(
        db: AsyncSession, department: str, year: int
    ) -> str:
        """Get next sequence number for equipment ID"""
        prefix = f"{settings.EQUIPMENT_ID_PREFIX}-{department[:4].upper()}-{year}-"

        result = await db.execute(
            select(func.count(EquipmentMaster.id)).where(
                EquipmentMaster.equipment_id.like(f"{prefix}%")
            )
        )
        count = result.scalar() or 0
        return f"{count + 1:03d}"

    @staticmethod
    def generate_qr_code(equipment_id: str, equipment_name: str) -> str:
        """
        Generate QR code for equipment
        Returns base64 encoded PNG image
        """
        qr_data = f"EQUIPMENT:{equipment_id}|{equipment_name}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    @staticmethod
    async def create_equipment(
        db: AsyncSession, equipment: EquipmentCreate, user_id: int
    ) -> EquipmentMaster:
        """Create new equipment"""
        # Generate equipment ID
        year = datetime.now().year
        sequence = await EquipmentService.get_next_sequence_number(
            db, equipment.department, year
        )
        equipment_id = f"{settings.EQUIPMENT_ID_PREFIX}-{equipment.department[:4].upper()}-{year}-{sequence}"

        # Generate equipment code
        equipment_code = f"{equipment.department[:3].upper()}-{equipment.equipment_name[:3].upper()}-{sequence}"

        # Create equipment
        db_equipment = EquipmentMaster(
            equipment_id=equipment_id,
            equipment_code=equipment_code,
            **equipment.model_dump(exclude={"specifications"}),
            created_by_id=user_id,
            updated_by_id=user_id,
        )

        # Generate QR code
        qr_code_data = EquipmentService.generate_qr_code(
            equipment_id, equipment.equipment_name
        )
        db_equipment.qr_code_data = qr_code_data

        db.add(db_equipment)
        await db.flush()

        # Add specifications
        if equipment.specifications:
            for spec in equipment.specifications:
                db_spec = EquipmentSpecification(
                    equipment_id=db_equipment.id, **spec.model_dump()
                )
                db.add(db_spec)

        # Add history entry
        history = EquipmentHistoryCard(
            equipment_id=db_equipment.id,
            event_date=datetime.now(),
            event_type="CREATION",
            description=f"Equipment {equipment_id} created",
            performed_by_id=user_id,
            after_status=equipment.status,
        )
        db.add(history)

        await db.commit()
        await db.refresh(db_equipment)

        return db_equipment

    @staticmethod
    async def get_equipment(
        db: AsyncSession, equipment_id: int
    ) -> Optional[EquipmentMaster]:
        """Get equipment by ID"""
        result = await db.execute(
            select(EquipmentMaster)
            .options(selectinload(EquipmentMaster.specifications))
            .where(EquipmentMaster.id == equipment_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_equipment(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        department: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[EquipmentMaster], int]:
        """List equipment with filters"""
        query = select(EquipmentMaster).options(
            selectinload(EquipmentMaster.specifications)
        )

        # Apply filters
        filters = []
        if department:
            filters.append(EquipmentMaster.department == department)
        if status:
            filters.append(EquipmentMaster.status == status)
        if category:
            filters.append(EquipmentMaster.category == category)
        if search:
            filters.append(
                or_(
                    EquipmentMaster.equipment_name.ilike(f"%{search}%"),
                    EquipmentMaster.equipment_id.ilike(f"%{search}%"),
                    EquipmentMaster.serial_number.ilike(f"%{search}%"),
                )
            )

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(func.count(EquipmentMaster.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(EquipmentMaster.created_at.desc())
        result = await db.execute(query)
        equipment_list = result.scalars().all()

        return equipment_list, total

    @staticmethod
    async def update_equipment(
        db: AsyncSession,
        equipment_id: int,
        equipment_update: EquipmentUpdate,
        user_id: int,
    ) -> Optional[EquipmentMaster]:
        """Update equipment"""
        db_equipment = await EquipmentService.get_equipment(db, equipment_id)
        if not db_equipment:
            return None

        # Track changes for history
        changes = []
        update_data = equipment_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            old_value = getattr(db_equipment, field)
            if old_value != value:
                changes.append(f"{field}: {old_value} -> {value}")
                setattr(db_equipment, field, value)

        db_equipment.updated_by_id = user_id

        # Add history entry
        if changes:
            history = EquipmentHistoryCard(
                equipment_id=equipment_id,
                event_date=datetime.now(),
                event_type="UPDATE",
                description=f"Equipment updated: {', '.join(changes)}",
                performed_by_id=user_id,
            )
            db.add(history)

        await db.commit()
        await db.refresh(db_equipment)

        return db_equipment

    @staticmethod
    async def calculate_oee(
        db: AsyncSession, equipment_id: int, start_date: date, end_date: date
    ) -> dict:
        """
        Calculate OEE (Overall Equipment Effectiveness) for equipment
        OEE = Availability × Performance × Quality
        """
        result = await db.execute(
            select(EquipmentUtilization).where(
                and_(
                    EquipmentUtilization.equipment_id == equipment_id,
                    EquipmentUtilization.date >= start_date,
                    EquipmentUtilization.date <= end_date,
                )
            )
        )
        records = result.scalars().all()

        if not records:
            return {
                "average_availability": 0,
                "average_performance": 0,
                "average_quality": 0,
                "average_oee": 0,
                "total_downtime_hours": 0,
                "breakdown_by_type": {},
            }

        total_availability = sum(
            (r.availability or 0) for r in records if r.availability
        )
        total_performance = sum((r.performance or 0) for r in records if r.performance)
        total_quality = sum((r.quality or 0) for r in records if r.quality)
        total_oee = sum((r.oee or 0) for r in records if r.oee)

        count = len(records)

        total_calibration_downtime = sum(
            (r.calibration_downtime or 0) for r in records
        )
        total_maintenance_downtime = sum(
            (r.maintenance_downtime or 0) for r in records
        )
        total_breakdown_downtime = sum((r.breakdown_downtime or 0) for r in records)
        total_idle_time = sum((r.idle_time or 0) for r in records)

        return {
            "average_availability": round(total_availability / count, 2) if count > 0 else 0,
            "average_performance": round(total_performance / count, 2) if count > 0 else 0,
            "average_quality": round(total_quality / count, 2) if count > 0 else 0,
            "average_oee": round(total_oee / count, 2) if count > 0 else 0,
            "total_downtime_hours": round(
                total_calibration_downtime
                + total_maintenance_downtime
                + total_breakdown_downtime,
                2,
            ),
            "breakdown_by_type": {
                "calibration": round(total_calibration_downtime, 2),
                "maintenance": round(total_maintenance_downtime, 2),
                "breakdown": round(total_breakdown_downtime, 2),
                "idle": round(total_idle_time, 2),
            },
        }

    @staticmethod
    def calculate_utilization_metrics(
        utilization: EquipmentUtilizationCreate,
    ) -> dict:
        """
        Calculate OEE metrics from utilization data
        """
        # Availability = (Planned Production Time - Downtime) / Planned Production Time
        availability = 0
        if utilization.planned_production_time and utilization.planned_production_time > 0:
            downtime = utilization.downtime or 0
            availability = (
                (utilization.planned_production_time - downtime)
                / utilization.planned_production_time
            ) * 100

        # Performance = (Ideal Cycle Time × Total Count) / Actual Production Time
        performance = 0
        if (
            utilization.ideal_cycle_time
            and utilization.total_count
            and utilization.actual_production_time
            and utilization.actual_production_time > 0
        ):
            performance = (
                (utilization.ideal_cycle_time * utilization.total_count)
                / utilization.actual_production_time
            ) * 100

        # Quality = Good Count / Total Count
        quality = 0
        if utilization.total_count and utilization.total_count > 0:
            good_count = utilization.good_count or 0
            quality = (good_count / utilization.total_count) * 100

        # OEE = Availability × Performance × Quality
        oee = (availability * performance * quality) / 10000  # Divide by 10000 because all are percentages

        return {
            "availability": round(Decimal(str(availability)), 2),
            "performance": round(Decimal(str(performance)), 2),
            "quality": round(Decimal(str(quality)), 2),
            "oee": round(Decimal(str(oee)), 2),
        }
