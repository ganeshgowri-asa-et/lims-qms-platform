"""
Equipment Calibration & Maintenance API (Session 3)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date, timedelta
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.equipment import Equipment, CalibrationRecord, PreventiveMaintenanceSchedule
from backend.models.common import AuditLog


router = APIRouter()


# Pydantic schemas
class EquipmentCreate(BaseModel):
    name: str
    manufacturer: str = None
    model: str = None
    serial_number: str = None
    location: str = None
    calibration_frequency_days: int = 365


class EquipmentResponse(BaseModel):
    id: int
    equipment_id: str
    name: str
    status: str
    next_calibration_date: date = None

    class Config:
        from_attributes = True


class CalibrationCreate(BaseModel):
    equipment_id: int
    calibration_date: date
    calibrated_by: str
    certificate_number: str = None
    result: str
    performed_by_id: int


@router.post("/", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    """Create new equipment with auto-generated EQP-ID"""

    # Generate equipment ID: EQP-XXX
    last_equipment = db.query(Equipment).order_by(Equipment.id.desc()).first()

    if last_equipment and last_equipment.equipment_id:
        last_num = int(last_equipment.equipment_id.split("-")[-1])
        equipment_id = f"EQP-{last_num + 1:03d}"
    else:
        equipment_id = "EQP-001"

    db_equipment = Equipment(
        equipment_id=equipment_id,
        name=equipment.name,
        manufacturer=equipment.manufacturer,
        model=equipment.model,
        serial_number=equipment.serial_number,
        location=equipment.location,
        calibration_frequency_days=equipment.calibration_frequency_days
    )

    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)

    return db_equipment


@router.get("/", response_model=List[EquipmentResponse])
def list_equipment(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all equipment"""
    equipment = db.query(Equipment).offset(skip).limit(limit).all()
    return equipment


@router.get("/calibration-due")
def get_calibration_due(days_ahead: int = 30, db: Session = Depends(get_db)):
    """Get equipment with calibration due within specified days"""
    target_date = date.today() + timedelta(days=days_ahead)

    equipment = db.query(Equipment).filter(
        Equipment.next_calibration_date <= target_date,
        Equipment.next_calibration_date >= date.today()
    ).all()

    return equipment


@router.post("/calibration", status_code=status.HTTP_201_CREATED)
def create_calibration_record(calibration: CalibrationCreate, db: Session = Depends(get_db)):
    """Create calibration record"""

    # Get equipment
    equipment = db.query(Equipment).filter(Equipment.id == calibration.equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    # Calculate next due date
    next_due = calibration.calibration_date + timedelta(days=equipment.calibration_frequency_days)

    # Create calibration record
    db_calibration = CalibrationRecord(
        equipment_id=calibration.equipment_id,
        calibration_date=calibration.calibration_date,
        next_due_date=next_due,
        calibrated_by=calibration.calibrated_by,
        certificate_number=calibration.certificate_number,
        result=calibration.result,
        performed_by_id=calibration.performed_by_id
    )

    # Update equipment
    equipment.last_calibration_date = calibration.calibration_date
    equipment.next_calibration_date = next_due

    db.add(db_calibration)
    db.commit()

    # Audit log
    audit_log = AuditLog(
        user_id=calibration.performed_by_id,
        module="equipment",
        action="calibrate",
        entity_type="calibration_records",
        entity_id=db_calibration.id,
        description=f"Calibrated equipment {equipment.equipment_id}"
    )
    db.add(audit_log)
    db.commit()

    return {"message": "Calibration record created", "next_due_date": next_due}


@router.get("/{equipment_id}/calibration-history")
def get_calibration_history(equipment_id: int, db: Session = Depends(get_db)):
    """Get calibration history for equipment"""
    records = db.query(CalibrationRecord).filter(
        CalibrationRecord.equipment_id == equipment_id
    ).order_by(CalibrationRecord.calibration_date.desc()).all()

    return records


@router.post("/maintenance")
def create_maintenance_schedule(
    equipment_id: int,
    maintenance_type: str,
    frequency_days: int,
    next_maintenance_date: date,
    db: Session = Depends(get_db)
):
    """Create preventive maintenance schedule"""

    schedule = PreventiveMaintenanceSchedule(
        equipment_id=equipment_id,
        maintenance_type=maintenance_type,
        frequency_days=frequency_days,
        next_maintenance_date=next_maintenance_date
    )

    db.add(schedule)
    db.commit()

    return {"message": "Maintenance schedule created"}
