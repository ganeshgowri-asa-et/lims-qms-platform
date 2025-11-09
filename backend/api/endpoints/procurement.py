"""
Procurement and Equipment API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.procurement import Equipment, Calibration, EquipmentStatusEnum
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime, timedelta

router = APIRouter()


class EquipmentCreate(BaseModel):
    name: str
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    calibration_required: bool = False
    calibration_frequency_days: Optional[int] = None


class EquipmentResponse(BaseModel):
    id: int
    equipment_id: str
    name: str
    category: Optional[str]
    status: str
    next_calibration_date: Optional[date]

    class Config:
        from_attributes = True


@router.post("/equipment", response_model=EquipmentResponse)
async def create_equipment(
    equipment: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register new equipment"""
    year = datetime.now().year
    count = db.query(Equipment).count() + 1
    equipment_id = f"EQ-{year}-{count:04d}"

    new_equipment = Equipment(
        equipment_id=equipment_id,
        name=equipment.name,
        category=equipment.category,
        manufacturer=equipment.manufacturer,
        model=equipment.model,
        serial_number=equipment.serial_number,
        calibration_required=equipment.calibration_required,
        calibration_frequency_days=equipment.calibration_frequency_days,
        status=EquipmentStatusEnum.ACTIVE,
        custodian_id=current_user.id,
        created_by_id=current_user.id
    )

    db.add(new_equipment)
    db.commit()
    db.refresh(new_equipment)

    return new_equipment


@router.get("/equipment", response_model=List[EquipmentResponse])
async def list_equipment(
    status: Optional[EquipmentStatusEnum] = None,
    calibration_due: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List equipment"""
    query = db.query(Equipment).filter(Equipment.is_deleted == False)

    if status:
        query = query.filter(Equipment.status == status)

    if calibration_due:
        today = date.today()
        query = query.filter(
            Equipment.calibration_required == True,
            Equipment.next_calibration_date <= today
        )

    equipment = query.offset(skip).limit(limit).all()
    return equipment


@router.get("/calibration/due", response_model=List[dict])
async def list_due_calibrations(
    days_ahead: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List equipment with calibration due in next N days"""
    today = date.today()
    future_date = today + timedelta(days=days_ahead)

    equipment = db.query(Equipment).filter(
        Equipment.calibration_required == True,
        Equipment.next_calibration_date <= future_date,
        Equipment.is_deleted == False
    ).all()

    return [
        {
            "equipment_id": e.equipment_id,
            "name": e.name,
            "next_calibration_date": str(e.next_calibration_date),
            "days_remaining": (e.next_calibration_date - today).days if e.next_calibration_date else None
        }
        for e in equipment
    ]
