"""
Maintenance management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.models.base import User
from app.models.maintenance import (
    PreventiveMaintenanceSchedule,
    MaintenanceRecord,
    EquipmentFailureLog,
    MaintenanceType,
    MaintenanceStatus,
)
from app.api.dependencies.auth import get_current_active_user
from pydantic import BaseModel

router = APIRouter()


# Pydantic schemas for maintenance
class MaintenanceScheduleCreate(BaseModel):
    equipment_id: int
    schedule_name: str
    description: Optional[str] = None
    frequency: str
    frequency_days: int
    start_date: date
    next_due_date: date
    checklist_items: Optional[dict] = None
    estimated_duration_hours: Optional[float] = None
    assigned_technician_id: Optional[int] = None


class MaintenanceRecordCreate(BaseModel):
    equipment_id: int
    schedule_id: Optional[int] = None
    maintenance_type: str
    priority: str = "medium"
    scheduled_date: Optional[date] = None
    problem_description: Optional[str] = None
    work_performed: Optional[str] = None
    parts_replaced: Optional[dict] = None
    parts_cost: Optional[float] = None
    labor_cost: Optional[float] = None
    service_cost: Optional[float] = None
    downtime_hours: Optional[float] = None


class EquipmentFailureCreate(BaseModel):
    equipment_id: int
    failure_type: str
    failure_description: str
    severity: str = "moderate"
    root_cause: Optional[str] = None
    downtime_hours: Optional[float] = None


# Preventive Maintenance Schedule Endpoints
@router.post("/schedules", status_code=status.HTTP_201_CREATED)
async def create_maintenance_schedule(
    schedule: MaintenanceScheduleCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create preventive maintenance schedule"""
    db_schedule = PreventiveMaintenanceSchedule(
        **schedule.model_dump(), created_by_id=current_user.id
    )

    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)

    return db_schedule


@router.get("/schedules")
async def list_maintenance_schedules(
    skip: int = 0,
    limit: int = 100,
    equipment_id: Optional[int] = None,
    active_only: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List preventive maintenance schedules"""
    query = select(PreventiveMaintenanceSchedule).offset(skip).limit(limit)

    if equipment_id:
        query = query.where(PreventiveMaintenanceSchedule.equipment_id == equipment_id)
    if active_only:
        query = query.where(PreventiveMaintenanceSchedule.is_active == True)

    result = await db.execute(query)
    schedules = result.scalars().all()

    return schedules


@router.get("/schedules/due")
async def get_maintenance_due(
    days_ahead: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get maintenance schedules due within specified days"""
    from datetime import timedelta

    today = date.today()
    due_date = today + timedelta(days=days_ahead)

    result = await db.execute(
        select(PreventiveMaintenanceSchedule).where(
            and_(
                PreventiveMaintenanceSchedule.next_due_date <= due_date,
                PreventiveMaintenanceSchedule.is_active == True,
            )
        )
    )
    schedules = result.scalars().all()

    return schedules


# Maintenance Records Endpoints
@router.post("/records", status_code=status.HTTP_201_CREATED)
async def create_maintenance_record(
    maintenance: MaintenanceRecordCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create maintenance record"""
    # Generate maintenance ID
    import random

    maintenance_id = f"MAINT-{maintenance.equipment_id:04d}-{datetime.now().year}-{random.randint(1, 999):03d}"

    # Calculate total cost
    total_cost = (
        (maintenance.parts_cost or 0)
        + (maintenance.labor_cost or 0)
        + (maintenance.service_cost or 0)
    )

    db_maintenance = MaintenanceRecord(
        maintenance_id=maintenance_id,
        total_cost=total_cost,
        status=MaintenanceStatus.SCHEDULED,
        performed_by_id=current_user.id,
        created_by_id=current_user.id,
        **maintenance.model_dump(),
    )

    db.add(db_maintenance)
    await db.commit()
    await db.refresh(db_maintenance)

    return db_maintenance


@router.get("/records")
async def list_maintenance_records(
    skip: int = 0,
    limit: int = 100,
    equipment_id: Optional[int] = None,
    maintenance_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List maintenance records"""
    query = select(MaintenanceRecord).offset(skip).limit(limit)

    filters = []
    if equipment_id:
        filters.append(MaintenanceRecord.equipment_id == equipment_id)
    if maintenance_type:
        filters.append(MaintenanceRecord.maintenance_type == maintenance_type)
    if status:
        filters.append(MaintenanceRecord.status == status)

    if filters:
        query = query.where(and_(*filters))

    result = await db.execute(query.order_by(MaintenanceRecord.created_at.desc()))
    records = result.scalars().all()

    return records


@router.get("/records/{maintenance_id}")
async def get_maintenance_record(
    maintenance_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get maintenance record by ID"""
    result = await db.execute(
        select(MaintenanceRecord).where(MaintenanceRecord.id == maintenance_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance record not found"
        )

    return record


@router.put("/records/{maintenance_id}/complete")
async def complete_maintenance(
    maintenance_id: int,
    work_performed: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark maintenance as completed"""
    result = await db.execute(
        select(MaintenanceRecord).where(MaintenanceRecord.id == maintenance_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance record not found"
        )

    record.status = MaintenanceStatus.COMPLETED
    record.work_performed = work_performed
    record.end_datetime = datetime.now()
    record.verified_by_id = current_user.id

    # Calculate duration if start time exists
    if record.start_datetime:
        duration = (record.end_datetime - record.start_datetime).total_seconds() / 3600
        record.actual_duration_hours = round(duration, 2)

    await db.commit()
    await db.refresh(record)

    return record


# Equipment Failure Log Endpoints
@router.post("/failures", status_code=status.HTTP_201_CREATED)
async def log_equipment_failure(
    failure: EquipmentFailureCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Log equipment failure"""
    db_failure = EquipmentFailureLog(
        failure_date=datetime.now(),
        created_by_id=current_user.id,
        **failure.model_dump(),
    )

    db.add(db_failure)
    await db.commit()
    await db.refresh(db_failure)

    return db_failure


@router.get("/failures")
async def list_equipment_failures(
    skip: int = 0,
    limit: int = 100,
    equipment_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List equipment failures"""
    query = select(EquipmentFailureLog).offset(skip).limit(limit)

    if equipment_id:
        query = query.where(EquipmentFailureLog.equipment_id == equipment_id)

    result = await db.execute(query.order_by(EquipmentFailureLog.failure_date.desc()))
    failures = result.scalars().all()

    return failures
