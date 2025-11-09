"""Equipment management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ....core.database import get_db
from ....schemas.equipment import (
    EquipmentMasterCreate,
    EquipmentMasterUpdate,
    EquipmentMasterResponse,
    CalibrationRecordCreate,
    CalibrationRecordResponse,
    MaintenanceScheduleCreate,
    MaintenanceScheduleUpdate,
    MaintenanceScheduleResponse,
    CalibrationAlert,
)
from ....services.equipment_service import EquipmentService
from ....utils.qr_generator import generate_qr_code

router = APIRouter()


# Equipment Master Endpoints
@router.post("/", response_model=EquipmentMasterResponse, status_code=201)
def create_equipment(
    equipment: EquipmentMasterCreate,
    db: Session = Depends(get_db)
):
    """Create new equipment with auto-generated equipment ID."""
    try:
        db_equipment = EquipmentService.create_equipment(db, equipment)

        # Generate QR code
        equipment_data = {
            "equipment_id": db_equipment.equipment_id,
            "name": db_equipment.name,
            "serial_number": db_equipment.serial_number or "",
            "location": db_equipment.location or "",
        }
        qr_path = f"/tmp/qr_codes/{db_equipment.equipment_id}.png"
        generate_qr_code(equipment_data, qr_path)

        # Update equipment with QR code path
        db_equipment.qr_code_path = qr_path
        db_equipment.qr_code_generated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_equipment)

        return db_equipment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[EquipmentMasterResponse])
def list_equipment(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of all equipment with pagination."""
    equipment = EquipmentService.get_all_equipment(db, skip=skip, limit=limit)
    return equipment


@router.get("/{equipment_id}", response_model=EquipmentMasterResponse)
def get_equipment(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    """Get specific equipment by ID."""
    equipment = EquipmentService.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@router.put("/{equipment_id}", response_model=EquipmentMasterResponse)
def update_equipment(
    equipment_id: int,
    updates: EquipmentMasterUpdate,
    db: Session = Depends(get_db)
):
    """Update equipment details."""
    equipment = EquipmentService.update_equipment(db, equipment_id, updates)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


# Calibration Endpoints
@router.post("/{equipment_id}/calibration", response_model=CalibrationRecordResponse, status_code=201)
def create_calibration_record(
    equipment_id: int,
    calibration: CalibrationRecordCreate,
    db: Session = Depends(get_db)
):
    """Create calibration record for equipment."""
    # Ensure equipment_id matches
    calibration.equipment_id = equipment_id

    # Verify equipment exists
    equipment = EquipmentService.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    try:
        db_calibration = EquipmentService.create_calibration_record(db, calibration)
        return db_calibration
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{equipment_id}/calibration", response_model=List[CalibrationRecordResponse])
def get_equipment_calibrations(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    """Get all calibration records for equipment."""
    calibrations = EquipmentService.get_equipment_calibrations(db, equipment_id)
    return calibrations


# Maintenance Endpoints
@router.post("/{equipment_id}/maintenance", response_model=MaintenanceScheduleResponse, status_code=201)
def create_maintenance_schedule(
    equipment_id: int,
    maintenance: MaintenanceScheduleCreate,
    db: Session = Depends(get_db)
):
    """Create maintenance schedule for equipment."""
    # Ensure equipment_id matches
    maintenance.equipment_id = equipment_id

    # Verify equipment exists
    equipment = EquipmentService.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    try:
        db_maintenance = EquipmentService.create_maintenance_schedule(db, maintenance)
        return db_maintenance
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/maintenance/{maintenance_id}", response_model=MaintenanceScheduleResponse)
def update_maintenance_record(
    maintenance_id: int,
    updates: MaintenanceScheduleUpdate,
    db: Session = Depends(get_db)
):
    """Update maintenance record (e.g., mark as completed)."""
    maintenance = EquipmentService.update_maintenance_record(db, maintenance_id, updates)
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return maintenance


@router.get("/{equipment_id}/maintenance", response_model=List[MaintenanceScheduleResponse])
def get_equipment_maintenance(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    """Get all maintenance records for equipment."""
    maintenance = EquipmentService.get_equipment_maintenance(db, equipment_id)
    return maintenance


# Alerts and Monitoring
@router.get("/alerts/calibration", response_model=List[CalibrationAlert])
def get_calibration_alerts(
    days: int = Query(30, description="Days threshold for alerts (7, 15, or 30)"),
    db: Session = Depends(get_db)
):
    """
    Get calibration due alerts.
    Supports 7-day (critical), 15-day (warning), and 30-day (info) thresholds.
    """
    alerts = EquipmentService.get_calibration_alerts(db, days_threshold=days)
    return alerts


@router.post("/{equipment_id}/calculate-oee", response_model=EquipmentMasterResponse)
def calculate_oee(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    """Calculate and update OEE metrics for equipment."""
    equipment = EquipmentService.calculate_oee(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@router.post("/{equipment_id}/generate-qr")
def generate_equipment_qr(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    """Generate or regenerate QR code for equipment."""
    equipment = EquipmentService.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    # Prepare equipment data
    equipment_data = {
        "equipment_id": equipment.equipment_id,
        "name": equipment.name,
        "serial_number": equipment.serial_number or "",
        "location": equipment.location or "",
    }

    # Generate QR code
    qr_path = f"/tmp/qr_codes/{equipment.equipment_id}.png"
    generate_qr_code(equipment_data, qr_path)

    # Update equipment
    equipment.qr_code_path = qr_path
    equipment.qr_code_generated_at = datetime.utcnow()
    db.commit()

    return {"message": "QR code generated successfully", "path": qr_path}
