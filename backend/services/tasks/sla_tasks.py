"""
SLA monitoring Celery tasks
"""
from backend.services.celery_app import celery_app
from backend.core.database import SessionLocal


@celery_app.task(name="backend.services.tasks.sla_tasks.check_sla_violations")
def check_sla_violations():
    """
    Periodic task to check for SLA violations
    """
    from backend.services.workflow_engine import WorkflowEngine

    db = SessionLocal()
    try:
        engine = WorkflowEngine(db)
        violations = engine.check_sla_violations()

        return {
            "violations_found": len(violations),
            "violations": [
                {
                    "id": v.id,
                    "entity_type": v.entity_type,
                    "entity_id": v.entity_id,
                    "severity": v.severity.value,
                    "violation_hours": v.violation_duration_hours
                }
                for v in violations
            ]
        }

    finally:
        db.close()


@celery_app.task(name="backend.services.tasks.sla_tasks.check_task_sla")
def check_task_sla():
    """
    Check SLA for tasks
    """
    from backend.models.workflow import Task, TaskStatusEnum, SLAViolation, RiskLevelEnum
    from datetime import datetime, timedelta

    db = SessionLocal()
    try:
        # Find overdue tasks
        today = datetime.now().date()

        overdue_tasks = db.query(Task).filter(
            Task.status.in_([TaskStatusEnum.TODO, TaskStatusEnum.IN_PROGRESS]),
            Task.due_date < today,
            Task.is_deleted == False
        ).all()

        violations = []
        for task in overdue_tasks:
            # Check if already logged
            existing = db.query(SLAViolation).filter(
                SLAViolation.task_id == task.id,
                SLAViolation.entity_type == "task"
            ).first()

            if not existing:
                days_overdue = (today - task.due_date).days
                violation_hours = days_overdue * 24

                # Calculate severity
                if days_overdue > 7:
                    severity = RiskLevelEnum.CRITICAL
                elif days_overdue > 3:
                    severity = RiskLevelEnum.HIGH
                elif days_overdue > 1:
                    severity = RiskLevelEnum.MEDIUM
                else:
                    severity = RiskLevelEnum.LOW

                violation = SLAViolation(
                    task_id=task.id,
                    entity_type="task",
                    entity_id=task.id,
                    sla_type="task_deadline",
                    expected_completion=datetime.combine(task.due_date, datetime.min.time()),
                    violation_duration_hours=violation_hours,
                    severity=severity,
                    created_by_id=task.created_by_id
                )

                db.add(violation)
                violations.append(violation)

        if violations:
            db.commit()

        return {
            "overdue_tasks": len(overdue_tasks),
            "violations_created": len(violations)
        }

    finally:
        db.close()
