"""
Analytics API (Session 9)
Provides data for dashboards and reporting
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date

from backend.core.database import get_db
from backend.models import *


router = APIRouter()


@router.get("/executive-dashboard")
def get_executive_dashboard(db: Session = Depends(get_db)):
    """
    Executive dashboard KPIs
    """

    # Test requests this month
    current_month = datetime.now().replace(day=1)
    test_requests_count = db.query(TestRequest).filter(
        TestRequest.request_date >= current_month.date()
    ).count()

    # Active NCs
    active_ncs = db.query(NonConformance).filter(
        NonConformance.status.in_(["open", "under_investigation", "capa_in_progress"])
    ).count()

    # Calibration due within 30 days
    cal_due = db.query(Equipment).filter(
        Equipment.next_calibration_date <= date.today() + timedelta(days=30),
        Equipment.next_calibration_date >= date.today()
    ).count()

    # Training compliance
    training_due = db.query(EmployeeTrainingMatrix).filter(
        EmployeeTrainingMatrix.next_due_date <= date.today() + timedelta(days=30)
    ).count()

    # Revenue (from test requests)
    revenue = db.query(func.sum(TestRequest.quotation_amount)).filter(
        TestRequest.request_date >= current_month.date()
    ).scalar() or 0

    return {
        "test_requests_this_month": test_requests_count,
        "active_nonconformances": active_ncs,
        "calibrations_due_30days": cal_due,
        "training_due_30days": training_due,
        "revenue_this_month": float(revenue),
        "updated_at": datetime.now().isoformat()
    }


@router.get("/quality-metrics")
def get_quality_metrics(db: Session = Depends(get_db)):
    """
    Quality metrics dashboard
    """

    # NC trend (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    nc_trend = db.query(
        func.strftime('%Y-%m', NonConformance.detected_date).label('month'),
        func.count(NonConformance.id).label('count')
    ).filter(
        NonConformance.detected_date >= six_months_ago.date()
    ).group_by('month').all()

    # CAPA effectiveness
    total_capas = db.query(CAPAAction).count()
    effective_capas = db.query(CAPAAction).filter(
        CAPAAction.effectiveness_result == "effective"
    ).count()

    capa_effectiveness_rate = (effective_capas / total_capas * 100) if total_capas > 0 else 0

    # Audit findings
    open_findings = db.query(AuditFinding).filter(
        AuditFinding.status == "open"
    ).count()

    # Risk distribution
    risks = db.query(
        RiskRegister.risk_level,
        func.count(RiskRegister.id).label('count')
    ).filter(
        RiskRegister.status == "active"
    ).group_by(RiskRegister.risk_level).all()

    risk_distribution = {risk.risk_level: risk.count for risk in risks}

    return {
        "nc_trend": [{"month": nc.month, "count": nc.count} for nc in nc_trend],
        "capa_effectiveness_rate": round(capa_effectiveness_rate, 2),
        "open_audit_findings": open_findings,
        "risk_distribution": risk_distribution
    }


@router.get("/operational-metrics")
def get_operational_metrics(db: Session = Depends(get_db)):
    """
    Operational metrics dashboard
    """

    # Equipment status
    equipment_status = db.query(
        Equipment.status,
        func.count(Equipment.id).label('count')
    ).group_by(Equipment.status).all()

    # Sample status
    sample_status = db.query(
        Sample.status,
        func.count(Sample.id).label('count')
    ).group_by(Sample.status).all()

    # Test completion rate
    total_requests = db.query(TestRequest).count()
    completed_requests = db.query(TestRequest).filter(
        TestRequest.status == "completed"
    ).count()

    completion_rate = (completed_requests / total_requests * 100) if total_requests > 0 else 0

    # Average test duration (placeholder - would calculate from actual data)
    avg_test_duration = 15.5  # days

    return {
        "equipment_status": {eq.status: eq.count for eq in equipment_status},
        "sample_status": {s.status: s.count for s in sample_status},
        "test_completion_rate": round(completion_rate, 2),
        "avg_test_duration_days": avg_test_duration
    }


@router.get("/customer-metrics")
def get_customer_metrics(db: Session = Depends(get_db)):
    """
    Customer-facing metrics
    """

    # Top customers by test requests
    top_customers = db.query(
        Customer.company_name,
        func.count(TestRequest.id).label('test_count')
    ).join(TestRequest).group_by(Customer.id).order_by(
        func.count(TestRequest.id).desc()
    ).limit(10).all()

    # Customer satisfaction (placeholder)
    customer_satisfaction_score = 4.5  # out of 5

    return {
        "top_customers": [
            {"company": c.company_name, "test_count": c.test_count}
            for c in top_customers
        ],
        "customer_satisfaction_score": customer_satisfaction_score
    }


@router.get("/traceability/{entity_type}/{entity_id}")
def get_traceability_trail(entity_type: str, entity_id: int, db: Session = Depends(get_db)):
    """
    Get end-to-end traceability for an entity
    """

    # Get audit logs
    audit_logs = db.query(AuditLog).filter(
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id
    ).order_by(AuditLog.timestamp.desc()).all()

    # Get related entities based on type
    related_entities = {}

    if entity_type == "samples":
        sample = db.query(Sample).filter(Sample.id == entity_id).first()
        if sample:
            related_entities["test_request"] = sample.test_request_id
            related_entities["test_results"] = [r.id for r in sample.test_results]

    elif entity_type == "nonconformances":
        nc = db.query(NonConformance).filter(NonConformance.id == entity_id).first()
        if nc:
            rca = db.query(RootCauseAnalysis).filter(RootCauseAnalysis.nc_id == entity_id).first()
            capas = db.query(CAPAAction).filter(CAPAAction.nc_id == entity_id).all()

            related_entities["root_cause_analysis"] = rca.id if rca else None
            related_entities["capa_actions"] = [c.id for c in capas]

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "audit_trail": [
            {
                "timestamp": log.timestamp.isoformat(),
                "user_id": log.user_id,
                "action": log.action,
                "description": log.description
            }
            for log in audit_logs
        ],
        "related_entities": related_entities
    }
