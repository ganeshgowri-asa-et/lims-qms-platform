"""
Analytics and Dashboard API endpoints - Comprehensive KPI & BI System
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, extract
from backend.core import get_db
from backend.models import *
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from backend.services.analytics_service import (
    KPICalculator, TrendAnalyzer, AnomalyDetector,
    BenchmarkAnalyzer, ReportGenerator
)
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel as PydanticBaseModel
import json
import io
from decimal import Decimal

router = APIRouter()


# Pydantic models for request/response
class DateRangeFilter(PydanticBaseModel):
    start_date: date
    end_date: date
    department: Optional[str] = None
    user_id: Optional[int] = None


class KPIDefinitionCreate(PydanticBaseModel):
    kpi_code: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    calculation_method: Optional[str] = None
    target_value: Optional[float] = None
    unit_of_measure: Optional[str] = None
    frequency: str = "Monthly"
    is_higher_better: bool = True
    department: Optional[str] = None


class KPIMeasurementCreate(PydanticBaseModel):
    kpi_definition_id: int
    measurement_date: date
    actual_value: float
    target_value: Optional[float] = None
    notes: Optional[str] = None


# =====================================================
# KPI DASHBOARD ENDPOINTS
# =====================================================

@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard statistics"""

    # Projects stats
    total_projects = db.query(Project).filter(Project.is_deleted == False).count()
    active_projects = db.query(Project).filter(
        Project.status == 'In Progress',
        Project.is_deleted == False
    ).count()

    # Tasks stats
    total_tasks = db.query(Task).filter(Task.is_deleted == False).count()
    my_tasks = db.query(Task).filter(
        Task.assigned_to_id == current_user.id,
        Task.is_deleted == False
    ).count()
    pending_tasks = db.query(Task).filter(
        Task.assigned_to_id == current_user.id,
        Task.status != 'Completed',
        Task.is_deleted == False
    ).count()

    # Documents stats
    total_documents = db.query(Document).filter(Document.is_deleted == False).count()
    pending_approvals = db.query(Document).filter(
        Document.approver_id == current_user.id,
        Document.status == 'In Review',
        Document.is_deleted == False
    ).count()

    # Quality stats
    open_ncs = db.query(NonConformance).filter(
        NonConformance.status == 'Open',
        NonConformance.is_deleted == False
    ).count()

    open_capas = db.query(CAPA).filter(
        CAPA.status == 'Open',
        CAPA.is_deleted == False
    ).count()

    # Calibration due
    calibration_due = db.query(Equipment).filter(
        Equipment.calibration_required == True,
        Equipment.next_calibration_date <= date.today() + timedelta(days=30),
        Equipment.is_deleted == False
    ).count()

    # Financial
    total_revenue = db.query(func.sum(Revenue.amount)).filter(
        Revenue.is_deleted == False
    ).scalar() or 0

    total_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.is_deleted == False
    ).scalar() or 0

    # CRM
    active_customers = db.query(Customer).filter(
        Customer.is_active == True,
        Customer.is_deleted == False
    ).count()

    pending_orders = db.query(Order).filter(
        Order.status.in_(['Confirmed', 'Processing', 'Testing']),
        Order.is_deleted == False
    ).count()

    return {
        "projects": {
            "total": total_projects,
            "active": active_projects
        },
        "tasks": {
            "total": total_tasks,
            "my_tasks": my_tasks,
            "pending": pending_tasks
        },
        "documents": {
            "total": total_documents,
            "pending_approvals": pending_approvals
        },
        "quality": {
            "open_ncs": open_ncs,
            "open_capas": open_capas
        },
        "equipment": {
            "calibration_due": calibration_due
        },
        "financial": {
            "total_revenue": float(total_revenue),
            "total_expenses": float(total_expenses),
            "net": float(total_revenue - total_expenses)
        },
        "crm": {
            "active_customers": active_customers,
            "pending_orders": pending_orders
        }
    }


@router.get("/kpis/dashboard")
async def get_kpi_dashboard(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    department: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive KPI dashboard with real-time metrics"""

    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    calculator = KPICalculator(db)

    kpis = {
        "document_approval_time": calculator.calculate_document_approval_time(start_date, end_date),
        "task_completion_rate": calculator.calculate_task_completion_rate(start_date, end_date, department),
        "workflow_cycle_time": calculator.calculate_workflow_cycle_time(start_date, end_date),
        "equipment_utilization": calculator.calculate_equipment_utilization(start_date, end_date),
        "test_turnaround_time": calculator.calculate_test_turnaround_time(start_date, end_date),
        "nonconformance_rate": calculator.calculate_nonconformance_rate(start_date, end_date),
        "customer_satisfaction": calculator.calculate_customer_satisfaction(start_date, end_date)
    }

    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "kpis": kpis
    }


@router.get("/kpis")
async def get_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Key Performance Indicators (legacy endpoint)"""

    today = datetime.now().date()
    last_month = today - timedelta(days=30)

    # Task completion rate
    completed_tasks = db.query(Task).filter(
        Task.status == 'Completed',
        Task.created_at >= str(last_month)
    ).count()
    total_tasks_last_month = db.query(Task).filter(
        Task.created_at >= str(last_month)
    ).count()
    task_completion_rate = (completed_tasks / total_tasks_last_month * 100) if total_tasks_last_month > 0 else 0

    # NC closure rate
    closed_ncs = db.query(NonConformance).filter(
        NonConformance.status == 'Closed',
        NonConformance.created_at >= str(last_month)
    ).count()
    total_ncs = db.query(NonConformance).filter(
        NonConformance.created_at >= str(last_month)
    ).count()
    nc_closure_rate = (closed_ncs / total_ncs * 100) if total_ncs > 0 else 0

    return {
        "task_completion_rate": round(task_completion_rate, 2),
        "nc_closure_rate": round(nc_closure_rate, 2),
        "active_projects": db.query(Project).filter(Project.status == 'In Progress').count(),
        "total_customers": db.query(Customer).filter(Customer.is_deleted == False).count()
    }


@router.post("/kpis/definitions")
async def create_kpi_definition(
    kpi_data: KPIDefinitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new KPI definition"""

    kpi = KPIDefinition(
        kpi_code=kpi_data.kpi_code,
        name=kpi_data.name,
        description=kpi_data.description,
        category=kpi_data.category,
        calculation_method=kpi_data.calculation_method,
        target_value=Decimal(str(kpi_data.target_value)) if kpi_data.target_value else None,
        unit_of_measure=kpi_data.unit_of_measure,
        frequency=kpi_data.frequency,
        is_higher_better=kpi_data.is_higher_better,
        department=kpi_data.department,
        owner_id=current_user.id,
        created_by_id=current_user.id
    )

    db.add(kpi)
    db.commit()
    db.refresh(kpi)

    return {"message": "KPI definition created", "kpi_id": kpi.id}


@router.get("/kpis/definitions")
async def list_kpi_definitions(
    category: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all KPI definitions"""

    query = db.query(KPIDefinition).filter(KPIDefinition.is_deleted == False)

    if category:
        query = query.filter(KPIDefinition.category == category)
    if department:
        query = query.filter(KPIDefinition.department == department)

    kpis = query.all()

    return {
        "kpis": [
            {
                "id": k.id,
                "kpi_code": k.kpi_code,
                "name": k.name,
                "category": k.category,
                "target_value": float(k.target_value) if k.target_value else None,
                "unit_of_measure": k.unit_of_measure,
                "frequency": k.frequency.value if k.frequency else None
            }
            for k in kpis
        ]
    }


@router.post("/kpis/measurements")
async def record_kpi_measurement(
    measurement_data: KPIMeasurementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a KPI measurement"""

    measurement = KPIMeasurement(
        kpi_definition_id=measurement_data.kpi_definition_id,
        measurement_date=measurement_data.measurement_date,
        actual_value=Decimal(str(measurement_data.actual_value)),
        target_value=Decimal(str(measurement_data.target_value)) if measurement_data.target_value else None,
        notes=measurement_data.notes,
        measured_by_id=current_user.id,
        created_by_id=current_user.id
    )

    # Calculate variance
    if measurement.target_value:
        measurement.variance = measurement.actual_value - measurement.target_value
        measurement.variance_percentage = (measurement.variance / measurement.target_value * 100) if measurement.target_value != 0 else Decimal('0')
        measurement.meets_target = measurement.actual_value >= measurement.target_value

    db.add(measurement)
    db.commit()
    db.refresh(measurement)

    return {"message": "KPI measurement recorded", "measurement_id": measurement.id}


@router.get("/kpis/{kpi_id}/trend")
async def get_kpi_trend(
    kpi_id: int,
    months: int = Query(12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trend analysis for a specific KPI"""

    analyzer = TrendAnalyzer(db)
    trend_data = analyzer.get_kpi_trend(kpi_id, months)

    return trend_data


@router.get("/kpis/{kpi_id}/forecast")
async def get_kpi_forecast(
    kpi_id: int,
    periods: int = Query(3),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get forecast for a specific KPI"""

    analyzer = TrendAnalyzer(db)
    forecast = analyzer.forecast_kpi(kpi_id, periods)

    return {"forecasts": forecast}


# =====================================================
# BUSINESS INTELLIGENCE ENDPOINTS
# =====================================================

@router.get("/bi/charts/nc-by-department")
async def get_nc_by_department(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get NC distribution by department for charts"""

    if not start_date:
        start_date = date.today() - timedelta(days=90)
    if not end_date:
        end_date = date.today()

    ncs = db.query(
        NonConformance.area_department,
        func.count(NonConformance.id).label('count')
    ).filter(
        and_(
            NonConformance.detected_date >= start_date,
            NonConformance.detected_date <= end_date,
            NonConformance.is_deleted == False
        )
    ).group_by(NonConformance.area_department).all()

    return {
        "chart_type": "bar",
        "data": [
            {"department": dept or "Unassigned", "count": count}
            for dept, count in ncs
        ]
    }


@router.get("/bi/charts/task-completion-trend")
async def get_task_completion_trend(
    months: int = Query(6),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get task completion trend over time"""

    end_date = date.today()
    start_date = end_date - timedelta(days=months * 30)

    # Group by month
    tasks_by_month = db.query(
        func.date_trunc('month', Task.created_at).label('month'),
        func.count(Task.id).label('total'),
        func.sum(case((Task.status == 'Completed', 1), else_=0)).label('completed')
    ).filter(
        and_(
            Task.created_at >= str(start_date),
            Task.created_at <= str(end_date),
            Task.is_deleted == False
        )
    ).group_by('month').order_by('month').all()

    return {
        "chart_type": "line",
        "data": [
            {
                "month": month.strftime('%Y-%m') if month else '',
                "total": total,
                "completed": completed,
                "completion_rate": round((completed / total * 100), 2) if total > 0 else 0
            }
            for month, total, completed in tasks_by_month
        ]
    }


@router.get("/bi/charts/revenue-vs-expenses")
async def get_revenue_vs_expenses(
    months: int = Query(12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get revenue vs expenses trend"""

    end_date = date.today()
    start_date = end_date - timedelta(days=months * 30)

    # Revenue by month
    revenue_by_month = db.query(
        func.date_trunc('month', Revenue.revenue_date).label('month'),
        func.sum(Revenue.amount).label('total_revenue')
    ).filter(
        and_(
            Revenue.revenue_date >= start_date,
            Revenue.revenue_date <= end_date,
            Revenue.is_deleted == False
        )
    ).group_by('month').order_by('month').all()

    # Expenses by month
    expenses_by_month = db.query(
        func.date_trunc('month', Expense.expense_date).label('month'),
        func.sum(Expense.amount).label('total_expense')
    ).filter(
        and_(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date,
            Expense.is_deleted == False
        )
    ).group_by('month').order_by('month').all()

    # Combine data
    revenue_dict = {month.strftime('%Y-%m') if month else '': float(amount) for month, amount in revenue_by_month}
    expense_dict = {month.strftime('%Y-%m') if month else '': float(amount) for month, amount in expenses_by_month}

    all_months = sorted(set(list(revenue_dict.keys()) + list(expense_dict.keys())))

    return {
        "chart_type": "line",
        "data": [
            {
                "month": month,
                "revenue": revenue_dict.get(month, 0),
                "expenses": expense_dict.get(month, 0),
                "profit": revenue_dict.get(month, 0) - expense_dict.get(month, 0)
            }
            for month in all_months
        ]
    }


@router.get("/bi/charts/equipment-utilization-heatmap")
async def get_equipment_utilization_heatmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get equipment utilization heatmap data"""

    equipment = db.query(Equipment).filter(Equipment.is_deleted == False).all()

    # Calculate utilization based on calibration frequency
    heatmap_data = []
    for eq in equipment:
        if eq.calibration_required and eq.last_calibration_date:
            days_since_calibration = (date.today() - eq.last_calibration_date).days
            # Simplified utilization metric
            utilization = max(0, 100 - (days_since_calibration / 365 * 100))
        else:
            utilization = 50  # Default for non-calibrated equipment

        heatmap_data.append({
            "equipment_id": eq.equipment_id,
            "name": eq.name,
            "utilization": round(utilization, 2)
        })

    return {
        "chart_type": "heatmap",
        "data": heatmap_data
    }


# =====================================================
# CONTINUAL IMPROVEMENT ENDPOINTS
# =====================================================

@router.post("/kaizen/suggestions")
async def create_kaizen_suggestion(
    suggestion_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a Kaizen suggestion"""

    # Generate suggestion number
    count = db.query(KaizenSuggestion).count()
    suggestion_number = f"KAIZEN-{date.today().year}-{count + 1:04d}"

    suggestion = KaizenSuggestion(
        suggestion_number=suggestion_number,
        title=suggestion_data['title'],
        description=suggestion_data['description'],
        current_situation=suggestion_data.get('current_situation'),
        proposed_improvement=suggestion_data['proposed_improvement'],
        expected_benefits=suggestion_data.get('expected_benefits'),
        category=suggestion_data.get('category'),
        area_department=suggestion_data.get('area_department'),
        submitted_by_id=current_user.id,
        submission_date=date.today(),
        created_by_id=current_user.id
    )

    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)

    return {"message": "Kaizen suggestion submitted", "suggestion_number": suggestion_number, "id": suggestion.id}


@router.get("/kaizen/suggestions")
async def list_kaizen_suggestions(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List Kaizen suggestions"""

    query = db.query(KaizenSuggestion).filter(KaizenSuggestion.is_deleted == False)

    if status:
        query = query.filter(KaizenSuggestion.status == status)
    if category:
        query = query.filter(KaizenSuggestion.category == category)

    suggestions = query.order_by(desc(KaizenSuggestion.submission_date)).all()

    return {
        "suggestions": [
            {
                "id": s.id,
                "suggestion_number": s.suggestion_number,
                "title": s.title,
                "status": s.status.value if s.status else None,
                "category": s.category,
                "submission_date": s.submission_date.isoformat() if s.submission_date else None,
                "submitted_by_id": s.submitted_by_id
            }
            for s in suggestions
        ]
    }


@router.post("/improvement/initiatives")
async def create_improvement_initiative(
    initiative_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an improvement initiative"""

    count = db.query(ImprovementInitiative).count()
    initiative_number = f"IMP-{date.today().year}-{count + 1:04d}"

    initiative = ImprovementInitiative(
        initiative_number=initiative_number,
        title=initiative_data['title'],
        description=initiative_data['description'],
        methodology=initiative_data['methodology'],
        problem_statement=initiative_data['problem_statement'],
        team_leader_id=current_user.id,
        start_date=date.today(),
        created_by_id=current_user.id
    )

    db.add(initiative)
    db.commit()
    db.refresh(initiative)

    return {"message": "Improvement initiative created", "initiative_number": initiative_number, "id": initiative.id}


@router.get("/improvement/initiatives")
async def list_improvement_initiatives(
    methodology: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List improvement initiatives"""

    query = db.query(ImprovementInitiative).filter(ImprovementInitiative.is_deleted == False)

    if methodology:
        query = query.filter(ImprovementInitiative.methodology == methodology)
    if status:
        query = query.filter(ImprovementInitiative.status == status)

    initiatives = query.order_by(desc(ImprovementInitiative.start_date)).all()

    return {
        "initiatives": [
            {
                "id": i.id,
                "initiative_number": i.initiative_number,
                "title": i.title,
                "methodology": i.methodology.value if i.methodology else None,
                "status": i.status.value if i.status else None,
                "start_date": i.start_date.isoformat() if i.start_date else None
            }
            for i in initiatives
        ]
    }


@router.post("/improvement/5why")
async def create_five_why_analysis(
    analysis_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a 5 Why analysis"""

    analysis = FiveWhyAnalysis(
        problem_statement=analysis_data['problem_statement'],
        initiative_id=analysis_data.get('initiative_id'),
        related_nc_id=analysis_data.get('related_nc_id'),
        why_1=analysis_data.get('why_1'),
        answer_1=analysis_data.get('answer_1'),
        why_2=analysis_data.get('why_2'),
        answer_2=analysis_data.get('answer_2'),
        why_3=analysis_data.get('why_3'),
        answer_3=analysis_data.get('answer_3'),
        why_4=analysis_data.get('why_4'),
        answer_4=analysis_data.get('answer_4'),
        why_5=analysis_data.get('why_5'),
        answer_5=analysis_data.get('answer_5'),
        root_cause=analysis_data.get('root_cause'),
        conducted_by_id=current_user.id,
        conducted_date=date.today(),
        created_by_id=current_user.id
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {"message": "5 Why analysis created", "id": analysis.id}


@router.post("/improvement/fishbone")
async def create_fishbone_diagram(
    fishbone_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a Fishbone diagram"""

    fishbone = FishboneDiagram(
        problem_statement=fishbone_data['problem_statement'],
        initiative_id=fishbone_data.get('initiative_id'),
        related_nc_id=fishbone_data.get('related_nc_id'),
        man_causes=fishbone_data.get('man_causes'),
        method_causes=fishbone_data.get('method_causes'),
        machine_causes=fishbone_data.get('machine_causes'),
        material_causes=fishbone_data.get('material_causes'),
        measurement_causes=fishbone_data.get('measurement_causes'),
        environment_causes=fishbone_data.get('environment_causes'),
        conducted_by_id=current_user.id,
        conducted_date=date.today(),
        created_by_id=current_user.id
    )

    db.add(fishbone)
    db.commit()
    db.refresh(fishbone)

    return {"message": "Fishbone diagram created", "id": fishbone.id}


@router.post("/improvement/fmea")
async def create_fmea_record(
    fmea_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an FMEA record"""

    count = db.query(FMEARecord).count()
    fmea_number = f"FMEA-{date.today().year}-{count + 1:04d}"

    # Calculate RPN
    severity = fmea_data.get('severity', 1)
    occurrence = fmea_data.get('occurrence', 1)
    detection = fmea_data.get('detection', 1)
    rpn = severity * occurrence * detection

    fmea = FMEARecord(
        fmea_number=fmea_number,
        title=fmea_data['title'],
        fmea_type=fmea_data.get('fmea_type'),
        process_name=fmea_data.get('process_name'),
        failure_mode=fmea_data['failure_mode'],
        potential_effects=fmea_data.get('potential_effects'),
        severity=severity,
        potential_causes=fmea_data.get('potential_causes'),
        occurrence=occurrence,
        current_detection_controls=fmea_data.get('current_detection_controls'),
        detection=detection,
        rpn=rpn,
        created_by_id=current_user.id
    )

    db.add(fmea)
    db.commit()
    db.refresh(fmea)

    return {"message": "FMEA record created", "fmea_number": fmea_number, "rpn": rpn, "id": fmea.id}


# =====================================================
# QUALITY OBJECTIVES & AUDIT ANALYTICS
# =====================================================

@router.post("/quality-objectives")
async def create_quality_objective(
    objective_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a quality objective"""

    count = db.query(QualityObjective).count()
    objective_number = f"QO-{date.today().year}-{count + 1:04d}"

    objective = QualityObjective(
        objective_number=objective_number,
        title=objective_data['title'],
        description=objective_data['description'],
        category=objective_data.get('category'),
        department=objective_data.get('department'),
        measurable_target=objective_data['measurable_target'],
        start_date=date.today(),
        owner_id=current_user.id,
        created_by_id=current_user.id
    )

    db.add(objective)
    db.commit()
    db.refresh(objective)

    return {"message": "Quality objective created", "objective_number": objective_number, "id": objective.id}


@router.get("/quality-objectives")
async def list_quality_objectives(
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List quality objectives"""

    query = db.query(QualityObjective).filter(QualityObjective.is_deleted == False)

    if status:
        query = query.filter(QualityObjective.status == status)
    if department:
        query = query.filter(QualityObjective.department == department)

    objectives = query.all()

    return {
        "objectives": [
            {
                "id": o.id,
                "objective_number": o.objective_number,
                "title": o.title,
                "status": o.status,
                "achievement_percentage": float(o.current_achievement_percentage) if o.current_achievement_percentage else 0,
                "target_date": o.target_date.isoformat() if o.target_date else None
            }
            for o in objectives
        ]
    }


@router.get("/audit-analytics")
async def get_audit_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive audit analytics"""

    if not start_date:
        start_date = date.today() - timedelta(days=365)
    if not end_date:
        end_date = date.today()

    audits = db.query(Audit).filter(
        and_(
            Audit.planned_date >= start_date,
            Audit.planned_date <= end_date,
            Audit.is_deleted == False
        )
    ).all()

    # Audit statistics
    total_audits = len(audits)
    by_type = {}
    by_status = {}

    for audit in audits:
        # By type
        audit_type = audit.audit_type.value if audit.audit_type else "Unknown"
        by_type[audit_type] = by_type.get(audit_type, 0) + 1

        # By status
        status = audit.status.value if audit.status else "Unknown"
        by_status[status] = by_status.get(status, 0) + 1

    # NC from audits
    ncs_from_audits = db.query(NonConformance).filter(
        NonConformance.audit_id.isnot(None),
        NonConformance.is_deleted == False
    ).count()

    return {
        "total_audits": total_audits,
        "by_type": by_type,
        "by_status": by_status,
        "ncs_generated": ncs_from_audits,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
    }


# =====================================================
# BENCHMARKING ENDPOINTS
# =====================================================

@router.post("/benchmarks")
async def create_benchmark(
    benchmark_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a benchmark entry"""

    benchmark = BenchmarkData(
        benchmark_name=benchmark_data['benchmark_name'],
        metric_name=benchmark_data['metric_name'],
        category=benchmark_data.get('category'),
        is_internal=benchmark_data.get('is_internal', True),
        benchmark_source=benchmark_data['benchmark_source'],
        benchmark_value=Decimal(str(benchmark_data['benchmark_value'])),
        unit_of_measure=benchmark_data.get('unit_of_measure'),
        our_value=Decimal(str(benchmark_data['our_value'])) if benchmark_data.get('our_value') else None,
        measurement_date=date.today(),
        created_by_id=current_user.id
    )

    # Calculate gap
    if benchmark.our_value:
        benchmark.gap = benchmark.our_value - benchmark.benchmark_value
        benchmark.gap_percentage = (benchmark.gap / benchmark.benchmark_value * 100) if benchmark.benchmark_value != 0 else Decimal('0')

    db.add(benchmark)
    db.commit()
    db.refresh(benchmark)

    return {"message": "Benchmark created", "id": benchmark.id}


@router.get("/benchmarks/compare")
async def compare_benchmarks(
    metric_name: str = Query(...),
    department: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare internal benchmarks"""

    analyzer = BenchmarkAnalyzer(db)

    if department:
        comparison = analyzer.compare_internal_benchmarks(metric_name, department)
        return comparison
    else:
        # List all benchmarks for this metric
        benchmarks = db.query(BenchmarkData).filter(
            BenchmarkData.metric_name == metric_name,
            BenchmarkData.is_deleted == False
        ).all()

        return {
            "metric_name": metric_name,
            "benchmarks": [
                {
                    "source": b.benchmark_source,
                    "value": float(b.benchmark_value),
                    "our_value": float(b.our_value) if b.our_value else None,
                    "gap": float(b.gap) if b.gap else None
                }
                for b in benchmarks
            ]
        }


# =====================================================
# AI-POWERED INSIGHTS
# =====================================================

@router.get("/ai/anomalies")
async def detect_anomalies(
    kpi_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detect anomalies in KPI data"""

    detector = AnomalyDetector(db)

    if kpi_id:
        anomalies = detector.detect_anomalies(kpi_id)
        return {"kpi_id": kpi_id, "anomalies": anomalies}
    else:
        # Get recent anomalies
        recent_anomalies = db.query(AnomalyDetection).filter(
            AnomalyDetection.acknowledged == False,
            AnomalyDetection.is_deleted == False
        ).order_by(desc(AnomalyDetection.detection_date)).limit(20).all()

        return {
            "anomalies": [
                {
                    "id": a.id,
                    "metric_name": a.metric_name,
                    "anomaly_type": a.anomaly_type,
                    "severity": a.severity,
                    "actual_value": float(a.actual_value),
                    "expected_value": float(a.expected_value) if a.expected_value else None,
                    "detection_date": a.detection_date.isoformat()
                }
                for a in recent_anomalies
            ]
        }


@router.post("/ai/anomalies/{anomaly_id}/acknowledge")
async def acknowledge_anomaly(
    anomaly_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Acknowledge an anomaly"""

    anomaly = db.query(AnomalyDetection).filter(AnomalyDetection.id == anomaly_id).first()

    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    anomaly.acknowledged = True
    anomaly.acknowledged_by_id = current_user.id
    anomaly.acknowledged_at = datetime.now()
    if notes:
        anomaly.investigation_notes = notes

    db.commit()

    return {"message": "Anomaly acknowledged"}


# =====================================================
# CUSTOM REPORTS & EXPORT
# =====================================================

@router.post("/reports/custom")
async def create_custom_report(
    report_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a custom report definition"""

    count = db.query(CustomReport).count()
    report_code = f"REPORT-{count + 1:04d}"

    report = CustomReport(
        report_code=report_code,
        report_name=report_data['report_name'],
        description=report_data.get('description'),
        category=report_data.get('category'),
        data_sources=report_data['data_sources'],
        filters=report_data.get('filters'),
        chart_type=report_data.get('chart_type'),
        created_by_id=current_user.id
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return {"message": "Custom report created", "report_code": report_code, "id": report.id}


@router.get("/reports/custom")
async def list_custom_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List custom reports"""

    reports = db.query(CustomReport).filter(
        or_(
            CustomReport.created_by_id == current_user.id,
            CustomReport.is_public == True
        ),
        CustomReport.is_deleted == False
    ).all()

    return {
        "reports": [
            {
                "id": r.id,
                "report_code": r.report_code,
                "report_name": r.report_name,
                "category": r.category,
                "is_public": r.is_public
            }
            for r in reports
        ]
    }


@router.get("/reports/executive-dashboard")
async def get_executive_dashboard(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate executive dashboard report"""

    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    generator = ReportGenerator(db)
    dashboard = generator.generate_executive_dashboard(start_date, end_date)

    return dashboard


@router.get("/reports/quality-metrics")
async def get_quality_metrics_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate quality metrics report"""

    if not start_date:
        start_date = date.today() - timedelta(days=90)
    if not end_date:
        end_date = date.today()

    generator = ReportGenerator(db)
    report = generator.generate_quality_metrics_report(start_date, end_date)

    return report


@router.get("/nc-analytics")
async def get_nc_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get enhanced NC analytics"""

    if not start_date:
        start_date = date.today() - timedelta(days=90)
    if not end_date:
        end_date = date.today()

    calculator = KPICalculator(db)
    nc_data = calculator.calculate_nonconformance_rate(start_date, end_date)

    # Additional NC analytics
    # Recurrence analysis
    ncs = db.query(NonConformance).filter(
        and_(
            NonConformance.detected_date >= start_date,
            NonConformance.detected_date <= end_date,
            NonConformance.is_deleted == False
        )
    ).all()

    # Group by process to find recurrences
    process_counts = {}
    for nc in ncs:
        if nc.process_affected:
            process_counts[nc.process_affected] = process_counts.get(nc.process_affected, 0) + 1

    recurring_processes = {k: v for k, v in process_counts.items() if v > 1}

    nc_data['recurring_processes'] = recurring_processes
    nc_data['period'] = {
        "start": start_date.isoformat(),
        "end": end_date.isoformat()
    }

    return nc_data


@router.get("/capa-analytics")
async def get_capa_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get CAPA effectiveness analytics"""

    if not start_date:
        start_date = date.today() - timedelta(days=180)
    if not end_date:
        end_date = date.today()

    capas = db.query(CAPA).filter(
        and_(
            CAPA.created_at >= str(start_date),
            CAPA.created_at <= str(end_date),
            CAPA.is_deleted == False
        )
    ).all()

    total_capas = len(capas)
    effective_capas = len([c for c in capas if c.is_effective == True])
    verified_capas = len([c for c in capas if c.status == CAPAStatusEnum.VERIFIED])

    effectiveness_rate = (effective_capas / verified_capas * 100) if verified_capas > 0 else 0

    # CAPA by type
    by_type = {"Corrective": 0, "Preventive": 0}
    for capa in capas:
        if capa.capa_type in by_type:
            by_type[capa.capa_type] += 1

    return {
        "total_capas": total_capas,
        "verified": verified_capas,
        "effective": effective_capas,
        "effectiveness_rate": round(effectiveness_rate, 2),
        "by_type": by_type,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
    }
