"""
Calibration service - Business logic for calibration management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.models.calibration import (
    CalibrationMaster,
    CalibrationRecord,
    CalibrationSchedule,
    CalibrationType,
    CalibrationResult,
)
from app.models.equipment import EquipmentMaster, CalibrationFrequency
from app.schemas.calibration import (
    CalibrationRecordCreate,
    CalibrationVendorCreate,
    CalibrationDueListResponse,
)
from app.core.config import settings


class CalibrationService:
    """Service for calibration management operations"""

    @staticmethod
    def calculate_next_calibration_date(
        last_calibration_date: date, frequency: CalibrationFrequency
    ) -> date:
        """
        Calculate next calibration due date based on frequency
        """
        frequency_days_map = {
            CalibrationFrequency.MONTHLY: 30,
            CalibrationFrequency.QUARTERLY: 90,
            CalibrationFrequency.HALF_YEARLY: 180,
            CalibrationFrequency.YEARLY: 365,
            CalibrationFrequency.BIENNIAL: 730,
        }

        days = frequency_days_map.get(frequency, 365)
        return last_calibration_date + timedelta(days=days)

    @staticmethod
    async def get_calibrations_due(
        db: AsyncSession, days_ahead: int = 30
    ) -> List[CalibrationDueListResponse]:
        """
        Get list of equipment with calibrations due within specified days
        """
        today = date.today()
        due_date = today + timedelta(days=days_ahead)

        result = await db.execute(
            select(EquipmentMaster).where(
                and_(
                    EquipmentMaster.requires_calibration == True,
                    EquipmentMaster.next_calibration_date <= due_date,
                    EquipmentMaster.is_active == True,
                )
            )
        )
        equipment_list = result.scalars().all()

        due_list = []
        for equipment in equipment_list:
            if equipment.next_calibration_date:
                days_until_due = (equipment.next_calibration_date - today).days

                # Determine alert level
                alert_level = "normal"
                if days_until_due < 0:
                    alert_level = "overdue"
                elif days_until_due <= settings.CALIBRATION_ALERT_DAYS_3:
                    alert_level = "7_days"
                elif days_until_due <= settings.CALIBRATION_ALERT_DAYS_2:
                    alert_level = "15_days"
                elif days_until_due <= settings.CALIBRATION_ALERT_DAYS_1:
                    alert_level = "30_days"

                due_list.append(
                    CalibrationDueListResponse(
                        equipment_id=equipment.id,
                        equipment_name=equipment.equipment_name,
                        equipment_code=equipment.equipment_code or "",
                        department=equipment.department,
                        next_calibration_date=equipment.next_calibration_date,
                        days_until_due=days_until_due,
                        calibration_frequency=equipment.calibration_frequency.value
                        if equipment.calibration_frequency
                        else "yearly",
                        last_calibration_date=equipment.last_calibration_date,
                        is_overdue=days_until_due < 0,
                        alert_level=alert_level,
                    )
                )

        # Sort by days until due (most urgent first)
        due_list.sort(key=lambda x: x.days_until_due)

        return due_list

    @staticmethod
    async def get_overdue_calibrations(
        db: AsyncSession,
    ) -> List[CalibrationDueListResponse]:
        """Get list of overdue calibrations"""
        today = date.today()

        result = await db.execute(
            select(EquipmentMaster).where(
                and_(
                    EquipmentMaster.requires_calibration == True,
                    EquipmentMaster.next_calibration_date < today,
                    EquipmentMaster.is_active == True,
                )
            )
        )
        equipment_list = result.scalars().all()

        overdue_list = []
        for equipment in equipment_list:
            if equipment.next_calibration_date:
                days_until_due = (equipment.next_calibration_date - today).days

                overdue_list.append(
                    CalibrationDueListResponse(
                        equipment_id=equipment.id,
                        equipment_name=equipment.equipment_name,
                        equipment_code=equipment.equipment_code or "",
                        department=equipment.department,
                        next_calibration_date=equipment.next_calibration_date,
                        days_until_due=days_until_due,
                        calibration_frequency=equipment.calibration_frequency.value
                        if equipment.calibration_frequency
                        else "yearly",
                        last_calibration_date=equipment.last_calibration_date,
                        is_overdue=True,
                        alert_level="overdue",
                    )
                )

        return overdue_list

    @staticmethod
    def generate_calibration_id(equipment_code: str, year: Optional[int] = None) -> str:
        """
        Generate unique calibration ID in format: CAL-EQPCODE-YYYY-XXX
        """
        if year is None:
            year = datetime.now().year

        sequence = "001"  # Should be incremented based on existing records

        return f"CAL-{equipment_code}-{year}-{sequence}"

    @staticmethod
    async def create_calibration_record(
        db: AsyncSession, calibration: CalibrationRecordCreate, user_id: int
    ) -> CalibrationRecord:
        """Create new calibration record"""
        # Get equipment to generate calibration ID
        equipment_result = await db.execute(
            select(EquipmentMaster).where(EquipmentMaster.id == calibration.equipment_id)
        )
        equipment = equipment_result.scalar_one_or_none()

        if not equipment:
            raise ValueError("Equipment not found")

        # Generate calibration ID
        year = calibration.calibration_date.year
        calibration_id = CalibrationService.generate_calibration_id(
            equipment.equipment_code or str(equipment.id), year
        )

        # Calculate next calibration date if equipment has frequency
        next_calibration_date = None
        if equipment.calibration_frequency:
            next_calibration_date = CalibrationService.calculate_next_calibration_date(
                calibration.calibration_date, equipment.calibration_frequency
            )

        # Calculate total cost
        total_cost = (calibration.calibration_cost or 0) + (
            calibration.additional_charges or 0
        )

        # Create calibration record
        db_calibration = CalibrationRecord(
            calibration_id=calibration_id,
            next_calibration_date=next_calibration_date,
            total_cost=total_cost,
            **calibration.model_dump(),
            created_by_id=user_id,
        )

        db.add(db_calibration)

        # Update equipment's last and next calibration dates
        equipment.last_calibration_date = calibration.calibration_date
        equipment.next_calibration_date = next_calibration_date

        await db.commit()
        await db.refresh(db_calibration)

        return db_calibration

    @staticmethod
    async def update_vendor_performance(
        db: AsyncSession, vendor_id: int, calibration_record: CalibrationRecord
    ):
        """Update vendor performance metrics"""
        vendor_result = await db.execute(
            select(CalibrationMaster).where(CalibrationMaster.id == vendor_id)
        )
        vendor = vendor_result.scalar_one_or_none()

        if not vendor:
            return

        # Update total calibrations
        vendor.total_calibrations += 1

        # Update on-time delivery metrics
        if calibration_record.turnaround_days:
            expected_days = 7  # Default expected turnaround
            if calibration_record.turnaround_days <= expected_days:
                vendor.on_time_delivery_count += 1
            else:
                vendor.delayed_delivery_count += 1

        # Calculate average turnaround days
        result = await db.execute(
            select(func.avg(CalibrationRecord.turnaround_days)).where(
                CalibrationRecord.vendor_id == vendor_id
            )
        )
        avg_turnaround = result.scalar()
        vendor.average_turnaround_days = (
            round(Decimal(str(avg_turnaround)), 2) if avg_turnaround else None
        )

        # Calculate quality rating based on pass/fail ratio
        pass_result = await db.execute(
            select(func.count(CalibrationRecord.id)).where(
                and_(
                    CalibrationRecord.vendor_id == vendor_id,
                    CalibrationRecord.result == CalibrationResult.PASS,
                )
            )
        )
        pass_count = pass_result.scalar() or 0

        if vendor.total_calibrations > 0:
            quality_rating = (pass_count / vendor.total_calibrations) * 5.0
            vendor.quality_rating = round(Decimal(str(quality_rating)), 2)

        await db.commit()

    @staticmethod
    async def create_calibration_schedule(
        db: AsyncSession, equipment_id: int
    ) -> Optional[CalibrationSchedule]:
        """
        Auto-create calibration schedule for equipment based on next calibration date
        """
        equipment_result = await db.execute(
            select(EquipmentMaster).where(EquipmentMaster.id == equipment_id)
        )
        equipment = equipment_result.scalar_one_or_none()

        if not equipment or not equipment.next_calibration_date:
            return None

        # Check if schedule already exists
        existing_result = await db.execute(
            select(CalibrationSchedule).where(
                and_(
                    CalibrationSchedule.equipment_id == equipment_id,
                    CalibrationSchedule.scheduled_date == equipment.next_calibration_date,
                    CalibrationSchedule.is_completed == False,
                )
            )
        )
        existing_schedule = existing_result.scalar_one_or_none()

        if existing_schedule:
            return existing_schedule

        # Create new schedule
        schedule = CalibrationSchedule(
            equipment_id=equipment_id,
            scheduled_date=equipment.next_calibration_date,
            calibration_type=CalibrationType.EXTERNAL,  # Default
        )

        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)

        return schedule

    @staticmethod
    async def check_and_update_alert_flags(
        db: AsyncSession,
    ) -> dict:
        """
        Check calibration due dates and update alert flags
        Returns dictionary with counts of alerts by level
        """
        today = date.today()

        alert_counts = {
            "30_days": 0,
            "15_days": 0,
            "7_days": 0,
            "overdue": 0,
        }

        # Get all active equipment requiring calibration
        result = await db.execute(
            select(EquipmentMaster).where(
                and_(
                    EquipmentMaster.requires_calibration == True,
                    EquipmentMaster.is_active == True,
                    EquipmentMaster.next_calibration_date.isnot(None),
                )
            )
        )
        equipment_list = result.scalars().all()

        for equipment in equipment_list:
            if not equipment.next_calibration_date:
                continue

            days_until_due = (equipment.next_calibration_date - today).days

            # Get or create schedule
            schedule_result = await db.execute(
                select(CalibrationSchedule).where(
                    and_(
                        CalibrationSchedule.equipment_id == equipment.id,
                        CalibrationSchedule.scheduled_date == equipment.next_calibration_date,
                        CalibrationSchedule.is_completed == False,
                    )
                )
            )
            schedule = schedule_result.scalar_one_or_none()

            if not schedule:
                schedule = CalibrationSchedule(
                    equipment_id=equipment.id,
                    scheduled_date=equipment.next_calibration_date,
                )
                db.add(schedule)
                await db.flush()

            # Update alert flags based on days until due
            if days_until_due < 0:
                schedule.is_overdue = True
                if not schedule.alert_overdue_sent:
                    alert_counts["overdue"] += 1
            elif days_until_due <= settings.CALIBRATION_ALERT_DAYS_3:
                if not schedule.alert_7_days_sent:
                    alert_counts["7_days"] += 1
            elif days_until_due <= settings.CALIBRATION_ALERT_DAYS_2:
                if not schedule.alert_15_days_sent:
                    alert_counts["15_days"] += 1
            elif days_until_due <= settings.CALIBRATION_ALERT_DAYS_1:
                if not schedule.alert_30_days_sent:
                    alert_counts["30_days"] += 1

        await db.commit()

        return alert_counts
