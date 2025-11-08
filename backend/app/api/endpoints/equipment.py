"""
Equipment management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.models.base import User
from app.schemas.equipment import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    EquipmentListResponse,
    EquipmentHistoryCreate,
    EquipmentHistoryResponse,
    EquipmentUtilizationCreate,
    EquipmentUtilizationResponse,
    OEECalculationResponse,
)
from app.services.equipment_service import EquipmentService
from app.api.dependencies.auth import get_current_active_user
from app.models.equipment import EquipmentHistoryCard, EquipmentUtilization
from sqlalchemy import select

router = APIRouter()


@router.post("/", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    equipment: EquipmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create new equipment"""
    db_equipment = await EquipmentService.create_equipment(
        db, equipment, current_user.id
    )
    return db_equipment


@router.get("/", response_model=EquipmentListResponse)
async def list_equipment(
    skip: int = 0,
    limit: int = 100,
    department: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List equipment with filters"""
    equipment_list, total = await EquipmentService.list_equipment(
        db,
        skip=skip,
        limit=limit,
        department=department,
        status=status,
        category=category,
        search=search,
    )

    return {
        "items": equipment_list,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit,
    }


@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get equipment by ID"""
    equipment = await EquipmentService.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found"
        )
    return equipment


@router.put("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: int,
    equipment_update: EquipmentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update equipment"""
    equipment = await EquipmentService.update_equipment(
        db, equipment_id, equipment_update, current_user.id
    )
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found"
        )
    return equipment


@router.get("/{equipment_id}/history", response_model=list[EquipmentHistoryResponse])
async def get_equipment_history(
    equipment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get equipment history"""
    result = await db.execute(
        select(EquipmentHistoryCard)
        .where(EquipmentHistoryCard.equipment_id == equipment_id)
        .order_by(EquipmentHistoryCard.event_date.desc())
    )
    history = result.scalars().all()
    return history


@router.post("/{equipment_id}/history", response_model=EquipmentHistoryResponse)
async def add_equipment_history(
    equipment_id: int,
    history: EquipmentHistoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add equipment history entry"""
    from datetime import datetime

    db_history = EquipmentHistoryCard(
        equipment_id=equipment_id,
        event_date=datetime.now(),
        event_type=history.event_type,
        description=history.description,
        performed_by_id=history.performed_by_id,
        verified_by_id=history.verified_by_id,
        before_status=history.before_status,
        after_status=history.after_status,
        downtime_hours=history.downtime_hours,
        cost=history.cost,
        supporting_documents=history.supporting_documents,
    )

    db.add(db_history)
    await db.commit()
    await db.refresh(db_history)

    return db_history


@router.post(
    "/{equipment_id}/utilization",
    response_model=EquipmentUtilizationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_utilization_record(
    equipment_id: int,
    utilization: EquipmentUtilizationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add equipment utilization record"""
    # Calculate OEE metrics
    metrics = EquipmentService.calculate_utilization_metrics(utilization)

    db_utilization = EquipmentUtilization(
        equipment_id=equipment_id,
        **utilization.model_dump(),
        **metrics,
    )

    db.add(db_utilization)
    await db.commit()
    await db.refresh(db_utilization)

    return db_utilization


@router.get("/{equipment_id}/oee", response_model=OEECalculationResponse)
async def calculate_equipment_oee(
    equipment_id: int,
    start_date: date = Query(..., description="Start date for OEE calculation"),
    end_date: date = Query(..., description="End date for OEE calculation"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate OEE for equipment over a date range"""
    equipment = await EquipmentService.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found"
        )

    oee_data = await EquipmentService.calculate_oee(db, equipment_id, start_date, end_date)

    return {
        "equipment_id": equipment_id,
        "equipment_name": equipment.equipment_name,
        "period_start": start_date,
        "period_end": end_date,
        **oee_data,
    }


@router.get("/{equipment_id}/qr-code")
async def get_qr_code(
    equipment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get equipment QR code"""
    equipment = await EquipmentService.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found"
        )

    if not equipment.qr_code_data:
        # Generate QR code if not exists
        qr_code_data = EquipmentService.generate_qr_code(
            equipment.equipment_id, equipment.equipment_name
        )
        equipment.qr_code_data = qr_code_data
        await db.commit()

    return {
        "equipment_id": equipment.equipment_id,
        "equipment_name": equipment.equipment_name,
        "qr_code_data": equipment.qr_code_data,
    }
