"""
Analytics and Dashboard API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.core import get_db
from backend.models import *
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics"""

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
    from datetime import date
    calibration_due = db.query(Equipment).filter(
        Equipment.calibration_required == True,
        Equipment.next_calibration_date <= date.today() + timedelta(days=30),
        Equipment.is_deleted == False
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
        }
    }


@router.get("/kpis")
async def get_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Key Performance Indicators"""

    # Calculate various KPIs
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
