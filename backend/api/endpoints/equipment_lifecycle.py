"""
Equipment Lifecycle Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.workflow import EquipmentLifecycleEvent, EquipmentLifecycleStageEnum
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime

router = APIRouter()


class EquipmentLifecycleEventCreate(BaseModel):
    equipment_id: int
    stage: EquipmentLifecycleStageEnum
    event_date: date
    description: Optional[str] = None
    rfq_id: Optional[int] = None
    po_id: Optional[int] = None
    installation_location: Optional[str] = None
    commissioning_report: Optional[str] = None
    fat_sat_report: Optional[str] = None
    calibration_id: Optional[int] = None
    maintenance_id: Optional[int] = None
    decommission_reason: Optional[str] = None
    cost: Optional[float] = None
    documents: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class EquipmentLifecycleEventResponse(BaseModel):
    id: int
    event_number: str
    equipment_id: int
    stage: str
    event_date: date
    description: Optional[str]

    class Config:
        from_attributes = True


@router.post("/", response_model=EquipmentLifecycleEventResponse)
async def create_lifecycle_event(
    event: EquipmentLifecycleEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new equipment lifecycle event"""
    year = datetime.now().year
    count = db.query(EquipmentLifecycleEvent).count() + 1
    event_number = f"EL-{year}-{count:06d}"

    new_event = EquipmentLifecycleEvent(
        event_number=event_number,
        equipment_id=event.equipment_id,
        stage=event.stage,
        event_date=event.event_date,
        description=event.description,
        performed_by_id=current_user.id,
        rfq_id=event.rfq_id,
        po_id=event.po_id,
        installation_location=event.installation_location,
        commissioning_report=event.commissioning_report,
        fat_sat_report=event.fat_sat_report,
        calibration_id=event.calibration_id,
        maintenance_id=event.maintenance_id,
        decommission_reason=event.decommission_reason,
        cost=event.cost,
        documents=event.documents,
        metadata=event.metadata,
        created_by_id=current_user.id
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    # Update equipment status based on lifecycle stage
    from backend.models.procurement import Equipment, EquipmentStatusEnum

    equipment = db.query(Equipment).get(event.equipment_id)
    if equipment:
        if event.stage == EquipmentLifecycleStageEnum.OPERATIONAL:
            equipment.status = EquipmentStatusEnum.ACTIVE
        elif event.stage == EquipmentLifecycleStageEnum.MAINTENANCE:
            equipment.status = EquipmentStatusEnum.UNDER_MAINTENANCE
        elif event.stage == EquipmentLifecycleStageEnum.CALIBRATION:
            equipment.status = EquipmentStatusEnum.UNDER_CALIBRATION
        elif event.stage in [EquipmentLifecycleStageEnum.DECOMMISSIONING, EquipmentLifecycleStageEnum.RETIRED]:
            equipment.status = EquipmentStatusEnum.RETIRED

        db.commit()

    return new_event


@router.get("/", response_model=List[EquipmentLifecycleEventResponse])
async def list_lifecycle_events(
    equipment_id: Optional[int] = None,
    stage: Optional[EquipmentLifecycleStageEnum] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List equipment lifecycle events"""
    query = db.query(EquipmentLifecycleEvent).filter(
        EquipmentLifecycleEvent.is_deleted == False
    )

    if equipment_id:
        query = query.filter(EquipmentLifecycleEvent.equipment_id == equipment_id)

    if stage:
        query = query.filter(EquipmentLifecycleEvent.stage == stage)

    events = query.order_by(EquipmentLifecycleEvent.event_date.desc()).offset(skip).limit(limit).all()
    return events


@router.get("/equipment/{equipment_id}/history")
async def get_equipment_lifecycle_history(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete lifecycle history of an equipment"""
    from backend.models.procurement import Equipment

    equipment = db.query(Equipment).get(equipment_id)

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    events = db.query(EquipmentLifecycleEvent).filter(
        EquipmentLifecycleEvent.equipment_id == equipment_id,
        EquipmentLifecycleEvent.is_deleted == False
    ).order_by(EquipmentLifecycleEvent.event_date).all()

    return {
        "equipment": {
            "id": equipment.id,
            "equipment_id": equipment.equipment_id,
            "name": equipment.name,
            "status": equipment.status.value if equipment.status else None
        },
        "lifecycle_events": [
            {
                "event_number": e.event_number,
                "stage": e.stage.value,
                "event_date": e.event_date.isoformat(),
                "description": e.description,
                "cost": e.cost,
                "performed_by_id": e.performed_by_id
            }
            for e in events
        ],
        "total_lifecycle_cost": sum(e.cost or 0 for e in events)
    }
