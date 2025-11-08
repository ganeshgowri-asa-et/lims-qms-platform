"""
Analytics and AI-powered insights endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.models.base import User
from app.services.ai_service import AIService
from app.services.calibration_service import CalibrationService
from app.api.dependencies.auth import get_current_active_user

router = APIRouter()


@router.get("/equipment/{equipment_id}/failure-prediction")
async def predict_equipment_failure(
    equipment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Predict probability of equipment failure in next 30 days using AI
    """
    prediction = await AIService.predict_failure_probability(db, equipment_id)
    return prediction


@router.get("/failure-patterns")
async def detect_failure_patterns(
    equipment_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Detect patterns in equipment failures using ML
    """
    patterns = await AIService.detect_failure_patterns(db, equipment_id)
    return {
        "patterns_detected": len(patterns),
        "patterns": patterns,
    }


@router.get("/equipment/{equipment_id}/calibration-recommendation")
async def recommend_calibration_frequency(
    equipment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    AI-powered recommendation for optimal calibration frequency
    """
    recommendation = await AIService.recommend_calibration_frequency(db, equipment_id)
    return recommendation


@router.get("/equipment/{equipment_id}/predictive-maintenance")
async def generate_predictive_maintenance(
    equipment_id: int,
    days_ahead: int = 90,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI-powered predictive maintenance schedule
    """
    schedule = await AIService.generate_predictive_maintenance_schedule(
        db, equipment_id, days_ahead
    )
    return {
        "equipment_id": equipment_id,
        "schedule_items": len(schedule),
        "schedule": schedule,
    }


@router.get("/calibration/alerts/check")
async def check_calibration_alerts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check and update calibration alert flags (30/15/7 days)
    Returns count of alerts by level
    """
    alert_counts = await CalibrationService.check_and_update_alert_flags(db)
    return {
        "alert_counts": alert_counts,
        "message": "Alert flags updated successfully",
    }


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get dashboard summary with key metrics
    """
    from sqlalchemy import select, func, and_
    from app.models.equipment import EquipmentMaster, EquipmentStatus
    from app.models.calibration import CalibrationRecord
    from app.models.maintenance import MaintenanceRecord, MaintenanceStatus
    from datetime import date, timedelta

    today = date.today()

    # Total equipment count
    total_equipment = await db.execute(
        select(func.count(EquipmentMaster.id)).where(EquipmentMaster.is_active == True)
    )
    total_equipment_count = total_equipment.scalar() or 0

    # Equipment by status
    operational = await db.execute(
        select(func.count(EquipmentMaster.id)).where(
            and_(
                EquipmentMaster.is_active == True,
                EquipmentMaster.status == EquipmentStatus.OPERATIONAL,
            )
        )
    )
    operational_count = operational.scalar() or 0

    # Calibrations due in 30 days
    calibrations_due = await CalibrationService.get_calibrations_due(db, 30)
    calibrations_due_count = len(calibrations_due)

    # Overdue calibrations
    overdue_calibrations = await CalibrationService.get_overdue_calibrations(db)
    overdue_count = len(overdue_calibrations)

    # Pending maintenance
    pending_maintenance = await db.execute(
        select(func.count(MaintenanceRecord.id)).where(
            MaintenanceRecord.status == MaintenanceStatus.SCHEDULED
        )
    )
    pending_maintenance_count = pending_maintenance.scalar() or 0

    # Recent calibrations (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    recent_calibrations = await db.execute(
        select(func.count(CalibrationRecord.id)).where(
            CalibrationRecord.calibration_date >= thirty_days_ago
        )
    )
    recent_calibrations_count = recent_calibrations.scalar() or 0

    return {
        "total_equipment": total_equipment_count,
        "operational_equipment": operational_count,
        "equipment_availability_rate": round(
            (operational_count / total_equipment_count * 100) if total_equipment_count > 0 else 0,
            2,
        ),
        "calibrations_due_30_days": calibrations_due_count,
        "overdue_calibrations": overdue_count,
        "pending_maintenance": pending_maintenance_count,
        "calibrations_last_30_days": recent_calibrations_count,
        "alerts": {
            "critical": overdue_count,
            "warning": calibrations_due_count,
        },
    }


@router.get("/reports/equipment-performance")
async def get_equipment_performance_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    department: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get equipment performance report with OEE metrics
    """
    from sqlalchemy import select, and_
    from app.models.equipment import EquipmentMaster, EquipmentUtilization
    from datetime import datetime, date, timedelta

    # Parse dates
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        start = date.today() - timedelta(days=30)

    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        end = date.today()

    # Get equipment
    query = select(EquipmentMaster).where(EquipmentMaster.is_active == True)
    if department:
        query = query.where(EquipmentMaster.department == department)

    equipment_result = await db.execute(query)
    equipment_list = equipment_result.scalars().all()

    # Calculate OEE for each equipment
    performance_data = []
    for equipment in equipment_list:
        oee_data = await AIService.prepare_equipment_data(
            db, equipment.id, lookback_days=(end - start).days
        )

        if len(oee_data) > 0:
            avg_oee = oee_data["oee"].mean() if "oee" in oee_data.columns else 0
            avg_availability = (
                oee_data["availability"].mean()
                if "availability" in oee_data.columns
                else 0
            )
            avg_performance = (
                oee_data["performance"].mean()
                if "performance" in oee_data.columns
                else 0
            )
            avg_quality = (
                oee_data["quality"].mean() if "quality" in oee_data.columns else 0
            )
        else:
            avg_oee = avg_availability = avg_performance = avg_quality = 0

        performance_data.append(
            {
                "equipment_id": equipment.id,
                "equipment_name": equipment.equipment_name,
                "department": equipment.department,
                "avg_oee": round(float(avg_oee), 2),
                "avg_availability": round(float(avg_availability), 2),
                "avg_performance": round(float(avg_performance), 2),
                "avg_quality": round(float(avg_quality), 2),
            }
        )

    # Sort by OEE
    performance_data.sort(key=lambda x: x["avg_oee"], reverse=True)

    return {
        "period": {"start_date": start.isoformat(), "end_date": end.isoformat()},
        "equipment_count": len(performance_data),
        "performance_data": performance_data,
    }


@router.get("/reports/calibration-summary")
async def get_calibration_summary_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get calibration summary report
    """
    from sqlalchemy import select, func, and_
    from app.models.calibration import CalibrationRecord, CalibrationResult
    from datetime import datetime, date, timedelta

    # Parse dates
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        start = date.today() - timedelta(days=90)

    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        end = date.today()

    # Total calibrations
    total_result = await db.execute(
        select(func.count(CalibrationRecord.id)).where(
            and_(
                CalibrationRecord.calibration_date >= start,
                CalibrationRecord.calibration_date <= end,
            )
        )
    )
    total_calibrations = total_result.scalar() or 0

    # Pass/Fail breakdown
    pass_result = await db.execute(
        select(func.count(CalibrationRecord.id)).where(
            and_(
                CalibrationRecord.calibration_date >= start,
                CalibrationRecord.calibration_date <= end,
                CalibrationRecord.result == CalibrationResult.PASS,
            )
        )
    )
    pass_count = pass_result.scalar() or 0

    fail_result = await db.execute(
        select(func.count(CalibrationRecord.id)).where(
            and_(
                CalibrationRecord.calibration_date >= start,
                CalibrationRecord.calibration_date <= end,
                CalibrationRecord.result == CalibrationResult.FAIL,
            )
        )
    )
    fail_count = fail_result.scalar() or 0

    # Average turnaround time
    avg_turnaround = await db.execute(
        select(func.avg(CalibrationRecord.turnaround_days)).where(
            and_(
                CalibrationRecord.calibration_date >= start,
                CalibrationRecord.calibration_date <= end,
            )
        )
    )
    avg_turnaround_days = avg_turnaround.scalar() or 0

    # Total cost
    total_cost = await db.execute(
        select(func.sum(CalibrationRecord.total_cost)).where(
            and_(
                CalibrationRecord.calibration_date >= start,
                CalibrationRecord.calibration_date <= end,
            )
        )
    )
    total_cost_value = total_cost.scalar() or 0

    return {
        "period": {"start_date": start.isoformat(), "end_date": end.isoformat()},
        "total_calibrations": total_calibrations,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "pass_rate": round((pass_count / total_calibrations * 100) if total_calibrations > 0 else 0, 2),
        "average_turnaround_days": round(float(avg_turnaround_days), 2),
        "total_cost": round(float(total_cost_value), 2),
    }
