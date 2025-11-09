"""Equipment management service with business logic."""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from ..models.equipment import (
    EquipmentMaster,
    CalibrationRecord,
    PreventiveMaintenanceSchedule,
    EquipmentStatus,
    CalibrationStatus,
)
from ..schemas.equipment import (
    EquipmentMasterCreate,
    EquipmentMasterUpdate,
    CalibrationRecordCreate,
    MaintenanceScheduleCreate,
    MaintenanceScheduleUpdate,
    CalibrationAlert,
)


class EquipmentService:
    """Service for equipment management operations."""

    @staticmethod
    def generate_equipment_id(db: Session) -> str:
        """
        Generate auto equipment ID in format: EQP-YYYY-XXXX
        where XXXX is a sequential number.
        """
        current_year = datetime.now().year

        # Get the count of equipment created this year
        count = db.query(EquipmentMaster).filter(
            EquipmentMaster.equipment_id.like(f"EQP-{current_year}-%")
        ).count()

        # Generate next number
        next_number = count + 1
        equipment_id = f"EQP-{current_year}-{next_number:04d}"

        return equipment_id

    @staticmethod
    def create_equipment(db: Session, equipment: EquipmentMasterCreate) -> EquipmentMaster:
        """Create new equipment with auto-generated ID."""
        # Generate equipment ID
        equipment_id = EquipmentService.generate_equipment_id(db)

        # Calculate next calibration date if required
        next_calibration_date = None
        if equipment.requires_calibration:
            if equipment.installation_date:
                next_calibration_date = equipment.installation_date + timedelta(
                    days=equipment.calibration_frequency_days
                )
            else:
                next_calibration_date = datetime.utcnow() + timedelta(
                    days=equipment.calibration_frequency_days
                )

        # Calculate next maintenance date
        next_maintenance_date = None
        if equipment.installation_date:
            next_maintenance_date = equipment.installation_date + timedelta(
                days=equipment.maintenance_frequency_days
            )
        else:
            next_maintenance_date = datetime.utcnow() + timedelta(
                days=equipment.maintenance_frequency_days
            )

        # Create equipment record
        db_equipment = EquipmentMaster(
            equipment_id=equipment_id,
            name=equipment.name,
            description=equipment.description,
            manufacturer=equipment.manufacturer,
            model_number=equipment.model_number,
            serial_number=equipment.serial_number,
            category=equipment.category,
            equipment_type=equipment.equipment_type,
            location=equipment.location,
            department=equipment.department,
            responsible_person=equipment.responsible_person,
            status=EquipmentStatus.OPERATIONAL,
            purchase_date=equipment.purchase_date,
            purchase_cost=equipment.purchase_cost,
            supplier=equipment.supplier,
            warranty_expiry=equipment.warranty_expiry,
            installation_date=equipment.installation_date,
            commissioned_date=equipment.commissioned_date,
            requires_calibration=equipment.requires_calibration,
            calibration_frequency_days=equipment.calibration_frequency_days,
            next_calibration_date=next_calibration_date,
            calibration_status=CalibrationStatus.DUE if equipment.requires_calibration else None,
            maintenance_frequency_days=equipment.maintenance_frequency_days,
            next_maintenance_date=next_maintenance_date,
            technical_specs=equipment.technical_specs,
            operating_range=equipment.operating_range,
        )

        db.add(db_equipment)
        db.commit()
        db.refresh(db_equipment)

        return db_equipment

    @staticmethod
    def update_equipment(
        db: Session, equipment_id: int, updates: EquipmentMasterUpdate
    ) -> Optional[EquipmentMaster]:
        """Update equipment details."""
        equipment = db.query(EquipmentMaster).filter(
            EquipmentMaster.id == equipment_id
        ).first()
        if not equipment:
            return None

        update_data = updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(equipment, field, value)

        db.commit()
        db.refresh(equipment)
        return equipment

    @staticmethod
    def create_calibration_record(
        db: Session, calibration: CalibrationRecordCreate
    ) -> CalibrationRecord:
        """Create calibration record and update equipment."""
        # Create calibration record
        db_calibration = CalibrationRecord(
            equipment_id=calibration.equipment_id,
            calibration_date=calibration.calibration_date,
            next_calibration_date=calibration.next_calibration_date,
            performed_by=calibration.performed_by,
            calibration_agency=calibration.calibration_agency,
            certificate_number=calibration.certificate_number,
            result=calibration.result,
            accuracy_achieved=calibration.accuracy_achieved,
            uncertainty=calibration.uncertainty,
            reference_standard=calibration.reference_standard,
            standard_certificate_number=calibration.standard_certificate_number,
            traceability=calibration.traceability,
            as_found_readings=calibration.as_found_readings,
            as_left_readings=calibration.as_left_readings,
            test_points=calibration.test_points,
            temperature=calibration.temperature,
            humidity=calibration.humidity,
            pressure=calibration.pressure,
            notes=calibration.notes,
            calibration_status=CalibrationStatus.COMPLETED,
        )

        db.add(db_calibration)

        # Update equipment calibration details
        equipment = db.query(EquipmentMaster).filter(
            EquipmentMaster.id == calibration.equipment_id
        ).first()

        if equipment:
            equipment.last_calibration_date = calibration.calibration_date
            equipment.next_calibration_date = calibration.next_calibration_date
            equipment.calibration_status = CalibrationStatus.COMPLETED

        db.commit()
        db.refresh(db_calibration)

        return db_calibration

    @staticmethod
    def create_maintenance_schedule(
        db: Session, maintenance: MaintenanceScheduleCreate
    ) -> PreventiveMaintenanceSchedule:
        """Create maintenance schedule."""
        db_maintenance = PreventiveMaintenanceSchedule(
            equipment_id=maintenance.equipment_id,
            maintenance_type=maintenance.maintenance_type,
            scheduled_date=maintenance.scheduled_date,
            maintenance_description=maintenance.maintenance_description,
            assigned_to=maintenance.assigned_to,
            checklist=maintenance.checklist,
        )

        db.add(db_maintenance)
        db.commit()
        db.refresh(db_maintenance)

        return db_maintenance

    @staticmethod
    def update_maintenance_record(
        db: Session, maintenance_id: int, updates: MaintenanceScheduleUpdate
    ) -> Optional[PreventiveMaintenanceSchedule]:
        """Update maintenance record."""
        maintenance = db.query(PreventiveMaintenanceSchedule).filter(
            PreventiveMaintenanceSchedule.id == maintenance_id
        ).first()

        if not maintenance:
            return None

        update_data = updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(maintenance, field, value)

        # Calculate total cost
        parts_cost = maintenance.parts_cost or 0
        labor_cost = maintenance.labor_cost or 0
        maintenance.total_cost = parts_cost + labor_cost

        # Update equipment maintenance date if completed
        if updates.is_completed and maintenance.equipment:
            equipment = maintenance.equipment
            equipment.last_maintenance_date = maintenance.completed_date
            # Calculate next maintenance date
            if maintenance.completed_date:
                equipment.next_maintenance_date = maintenance.completed_date + timedelta(
                    days=equipment.maintenance_frequency_days
                )

        db.commit()
        db.refresh(maintenance)

        return maintenance

    @staticmethod
    def get_calibration_alerts(db: Session, days_threshold: int = 30) -> List[CalibrationAlert]:
        """Get calibration due alerts (30/15/7 days)."""
        today = datetime.utcnow()
        threshold_date = today + timedelta(days=days_threshold)

        equipment_list = db.query(EquipmentMaster).filter(
            EquipmentMaster.requires_calibration == True,
            EquipmentMaster.next_calibration_date <= threshold_date,
            EquipmentMaster.status != EquipmentStatus.RETIRED,
        ).all()

        alerts = []
        for equipment in equipment_list:
            if equipment.next_calibration_date:
                days_remaining = (equipment.next_calibration_date - today).days

                # Determine alert level
                if days_remaining < 0:
                    alert_level = "overdue"
                elif days_remaining <= 7:
                    alert_level = "critical"
                elif days_remaining <= 15:
                    alert_level = "warning"
                else:
                    alert_level = "info"

                alerts.append(
                    CalibrationAlert(
                        equipment_id=equipment.equipment_id,
                        equipment_name=equipment.name,
                        next_calibration_date=equipment.next_calibration_date,
                        days_remaining=days_remaining,
                        alert_level=alert_level,
                    )
                )

        return alerts

    @staticmethod
    def calculate_oee(db: Session, equipment_id: int) -> Optional[EquipmentMaster]:
        """Calculate and update OEE metrics."""
        equipment = db.query(EquipmentMaster).filter(
            EquipmentMaster.id == equipment_id
        ).first()

        if not equipment:
            return None

        # Calculate availability
        if equipment.planned_uptime_hours > 0:
            equipment.availability_percentage = (
                equipment.actual_uptime_hours / equipment.planned_uptime_hours
            ) * 100
        else:
            equipment.availability_percentage = 100.0

        # OEE = Availability × Performance × Quality
        equipment.oee_percentage = (
            equipment.availability_percentage
            * equipment.performance_percentage
            * equipment.quality_percentage
        ) / 10000  # Divide by 10000 because we multiply three percentages

        db.commit()
        db.refresh(equipment)

        return equipment

    @staticmethod
    def get_equipment(db: Session, equipment_id: int) -> Optional[EquipmentMaster]:
        """Get equipment by ID."""
        return db.query(EquipmentMaster).filter(EquipmentMaster.id == equipment_id).first()

    @staticmethod
    def get_all_equipment(db: Session, skip: int = 0, limit: int = 100) -> List[EquipmentMaster]:
        """Get all equipment with pagination."""
        return db.query(EquipmentMaster).offset(skip).limit(limit).all()

    @staticmethod
    def get_equipment_calibrations(db: Session, equipment_id: int) -> List[CalibrationRecord]:
        """Get all calibration records for equipment."""
        return (
            db.query(CalibrationRecord)
            .filter(CalibrationRecord.equipment_id == equipment_id)
            .order_by(CalibrationRecord.calibration_date.desc())
            .all()
        )

    @staticmethod
    def get_equipment_maintenance(
        db: Session, equipment_id: int
    ) -> List[PreventiveMaintenanceSchedule]:
        """Get all maintenance records for equipment."""
        return (
            db.query(PreventiveMaintenanceSchedule)
            .filter(PreventiveMaintenanceSchedule.equipment_id == equipment_id)
            .order_by(PreventiveMaintenanceSchedule.scheduled_date.desc())
            .all()
        )
