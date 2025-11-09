"""
Analytics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta
from typing import List, Dict, Any
from backend.database import get_db
from backend.models import (
    TestRequest, Sample, NonConformance, AuditFinding,
    CalibrationRecord, TrainingAttendance, AnalyticsKPI
)

router = APIRouter()


@router.get("/kpis/executive")
async def get_executive_kpis(db: Session = Depends(get_db)):
    """Get executive dashboard KPIs"""

    # Get date ranges
    today = datetime.now().date()
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)
    last_month = (start_of_month - timedelta(days=1)).replace(day=1)

    # Total test requests this month
    test_requests_current = db.query(func.count(TestRequest.id)).filter(
        TestRequest.request_date >= start_of_month
    ).scalar() or 0

    test_requests_last = db.query(func.count(TestRequest.id)).filter(
        TestRequest.request_date >= last_month,
        TestRequest.request_date < start_of_month
    ).scalar() or 0

    # Revenue (from approved quotes)
    revenue_current = db.query(func.sum(TestRequest.quote_amount)).filter(
        TestRequest.request_date >= start_of_month,
        TestRequest.quote_approved == True
    ).scalar() or 0

    revenue_last = db.query(func.sum(TestRequest.quote_amount)).filter(
        TestRequest.request_date >= last_month,
        TestRequest.request_date < start_of_month,
        TestRequest.quote_approved == True
    ).scalar() or 0

    # Active samples
    active_samples = db.query(func.count(Sample.id)).filter(
        Sample.status.in_(['Received', 'In Progress', 'Testing'])
    ).scalar() or 0

    # Non-conformances this month
    nc_current = db.query(func.count(NonConformance.id)).filter(
        NonConformance.nc_date >= start_of_month
    ).scalar() or 0

    # Quality rate (samples without NCs vs total samples)
    total_samples = db.query(func.count(Sample.id)).filter(
        Sample.received_date >= start_of_month
    ).scalar() or 1  # Avoid division by zero

    quality_rate = ((total_samples - nc_current) / total_samples) * 100 if total_samples > 0 else 100

    # On-time delivery rate
    completed_requests = db.query(TestRequest).filter(
        TestRequest.request_date >= start_of_month,
        TestRequest.status == 'Completed'
    ).all()

    on_time = sum(1 for req in completed_requests
                  if req.required_date and req.updated_at.date() <= req.required_date)
    total_completed = len(completed_requests)
    on_time_rate = (on_time / total_completed * 100) if total_completed > 0 else 0

    return {
        "test_requests": {
            "current": test_requests_current,
            "previous": test_requests_last,
            "change_percent": ((test_requests_current - test_requests_last) / test_requests_last * 100)
                if test_requests_last > 0 else 0
        },
        "revenue": {
            "current": float(revenue_current),
            "previous": float(revenue_last),
            "change_percent": ((revenue_current - revenue_last) / revenue_last * 100)
                if revenue_last > 0 else 0
        },
        "active_samples": active_samples,
        "quality_rate": round(quality_rate, 2),
        "on_time_delivery": round(on_time_rate, 2),
        "non_conformances": nc_current
    }


@router.get("/kpis/operational")
async def get_operational_kpis(db: Session = Depends(get_db)):
    """Get operational dashboard KPIs"""

    today = datetime.now().date()
    start_of_month = today.replace(day=1)

    # Sample turnaround time
    completed_samples = db.query(Sample).filter(
        Sample.received_date >= start_of_month,
        Sample.status == 'Completed'
    ).all()

    avg_turnaround = 0
    if completed_samples:
        turnaround_times = []
        for sample in completed_samples:
            # Calculate days between received and completed
            # This is simplified - in real system you'd have a completion_date field
            days = 7  # Placeholder
            turnaround_times.append(days)
        avg_turnaround = sum(turnaround_times) / len(turnaround_times)

    # Equipment calibration status
    total_equipment = db.query(func.count(CalibrationRecord.equipment_id.distinct())).scalar() or 0
    overdue_calibrations = db.query(func.count(CalibrationRecord.equipment_id.distinct())).filter(
        CalibrationRecord.next_due_date < today
    ).scalar() or 0

    # Training compliance
    total_trainings = db.query(func.count(TrainingAttendance.id)).filter(
        TrainingAttendance.training_date >= start_of_month
    ).scalar() or 0

    completed_trainings = db.query(func.count(TrainingAttendance.id)).filter(
        TrainingAttendance.training_date >= start_of_month,
        TrainingAttendance.status == 'Completed'
    ).scalar() or 0

    training_compliance = (completed_trainings / total_trainings * 100) if total_trainings > 0 else 0

    # Sample status distribution
    status_distribution = db.query(
        Sample.status,
        func.count(Sample.id)
    ).filter(
        Sample.received_date >= start_of_month
    ).group_by(Sample.status).all()

    return {
        "avg_turnaround_days": round(avg_turnaround, 1),
        "equipment_calibration": {
            "total": total_equipment,
            "overdue": overdue_calibrations,
            "compliance_rate": ((total_equipment - overdue_calibrations) / total_equipment * 100)
                if total_equipment > 0 else 100
        },
        "training_compliance": round(training_compliance, 2),
        "sample_status_distribution": [
            {"status": status, "count": count}
            for status, count in status_distribution
        ]
    }


@router.get("/kpis/quality")
async def get_quality_kpis(db: Session = Depends(get_db)):
    """Get quality dashboard KPIs"""

    today = datetime.now().date()
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    # Non-conformance trend (last 6 months)
    nc_trend = []
    for i in range(6, 0, -1):
        month_start = (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        count = db.query(func.count(NonConformance.id)).filter(
            NonConformance.nc_date >= month_start,
            NonConformance.nc_date <= month_end
        ).scalar() or 0

        nc_trend.append({
            "month": month_start.strftime("%Y-%m"),
            "count": count
        })

    # NC by severity
    nc_by_severity = db.query(
        NonConformance.severity,
        func.count(NonConformance.id)
    ).filter(
        NonConformance.nc_date >= start_of_year
    ).group_by(NonConformance.severity).all()

    # CAPA effectiveness
    total_nc = db.query(func.count(NonConformance.id)).filter(
        NonConformance.nc_date >= start_of_year
    ).scalar() or 0

    closed_nc = db.query(func.count(NonConformance.id)).filter(
        NonConformance.nc_date >= start_of_year,
        NonConformance.status == 'Closed'
    ).scalar() or 0

    capa_effectiveness = (closed_nc / total_nc * 100) if total_nc > 0 else 0

    # Audit findings
    total_findings = db.query(func.count(AuditFinding.id)).filter(
        AuditFinding.finding_date >= start_of_year
    ).scalar() or 0

    findings_by_type = db.query(
        AuditFinding.finding_type,
        func.count(AuditFinding.id)
    ).filter(
        AuditFinding.finding_date >= start_of_year
    ).group_by(AuditFinding.finding_type).all()

    return {
        "nc_trend": nc_trend,
        "nc_by_severity": [
            {"severity": severity, "count": count}
            for severity, count in nc_by_severity
        ],
        "capa_effectiveness": round(capa_effectiveness, 2),
        "audit_findings": {
            "total": total_findings,
            "by_type": [
                {"type": finding_type, "count": count}
                for finding_type, count in findings_by_type
            ]
        }
    }


@router.get("/trends/test-volume")
async def get_test_volume_trend(
    months: int = 12,
    db: Session = Depends(get_db)
):
    """Get test volume trend over time"""

    today = datetime.now().date()
    trend_data = []

    for i in range(months, 0, -1):
        month_start = (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        count = db.query(func.count(TestRequest.id)).filter(
            TestRequest.request_date >= month_start,
            TestRequest.request_date <= month_end
        ).scalar() or 0

        revenue = db.query(func.sum(TestRequest.quote_amount)).filter(
            TestRequest.request_date >= month_start,
            TestRequest.request_date <= month_end,
            TestRequest.quote_approved == True
        ).scalar() or 0

        trend_data.append({
            "month": month_start.strftime("%Y-%m"),
            "test_requests": count,
            "revenue": float(revenue)
        })

    return trend_data


@router.get("/trends/quality-metrics")
async def get_quality_metrics_trend(
    months: int = 12,
    db: Session = Depends(get_db)
):
    """Get quality metrics trend over time"""

    today = datetime.now().date()
    trend_data = []

    for i in range(months, 0, -1):
        month_start = (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # NC count
        nc_count = db.query(func.count(NonConformance.id)).filter(
            NonConformance.nc_date >= month_start,
            NonConformance.nc_date <= month_end
        ).scalar() or 0

        # Sample count
        sample_count = db.query(func.count(Sample.id)).filter(
            Sample.received_date >= month_start,
            Sample.received_date <= month_end
        ).scalar() or 1  # Avoid division by zero

        # Quality rate
        quality_rate = ((sample_count - nc_count) / sample_count * 100) if sample_count > 0 else 100

        trend_data.append({
            "month": month_start.strftime("%Y-%m"),
            "nc_count": nc_count,
            "sample_count": sample_count,
            "quality_rate": round(quality_rate, 2)
        })

    return trend_data
