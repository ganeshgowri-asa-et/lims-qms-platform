"""
Workflow-related Celery tasks
"""
from backend.services.celery_app import celery_app
from backend.core.database import SessionLocal
from backend.models.procurement import Equipment, Calibration
from backend.models.workflow import EquipmentLifecycleEvent, EquipmentLifecycleStageEnum
from datetime import datetime, timedelta
from sqlalchemy import and_


@celery_app.task(name="backend.services.tasks.workflow_tasks.update_calibration_schedules")
def update_calibration_schedules():
    """
    Daily task to check for upcoming calibrations and create reminders
    """
    db = SessionLocal()
    try:
        # Find equipment with upcoming calibration
        today = datetime.now().date()
        upcoming_days = 30  # Alert 30 days before

        equipment_list = db.query(Equipment).filter(
            and_(
                Equipment.calibration_required == True,
                Equipment.next_calibration_date.isnot(None),
                Equipment.next_calibration_date <= today + timedelta(days=upcoming_days),
                Equipment.next_calibration_date >= today
            )
        ).all()

        notifications = []
        for equip in equipment_list:
            days_until = (equip.next_calibration_date - today).days

            # Create notification (would integrate with notification system)
            notifications.append({
                "equipment_id": equip.id,
                "equipment_name": equip.name,
                "calibration_due": equip.next_calibration_date.isoformat(),
                "days_until": days_until,
                "custodian_id": equip.custodian_id
            })

        return {
            "checked": len(equipment_list),
            "notifications_created": len(notifications)
        }

    finally:
        db.close()


@celery_app.task(name="backend.services.tasks.workflow_tasks.auto_advance_workflow")
def auto_advance_workflow(instance_id: int, action: str, data: dict = None):
    """
    Automatically advance workflow based on automation rules
    """
    from backend.services.workflow_engine import WorkflowEngine

    db = SessionLocal()
    try:
        engine = WorkflowEngine(db)
        instance = engine.advance_workflow(
            instance_id=instance_id,
            action=action,
            user_id=1,  # System user
            data=data,
            comments="Auto-advanced by system"
        )

        return {
            "instance_id": instance.id,
            "status": instance.status.value,
            "current_step": instance.current_step
        }

    finally:
        db.close()


@celery_app.task(name="backend.services.tasks.workflow_tasks.process_equipment_lifecycle")
def process_equipment_lifecycle(equipment_id: int, stage: str, event_data: dict):
    """
    Process equipment lifecycle stage transitions
    """
    db = SessionLocal()
    try:
        from datetime import datetime

        # Generate event number
        year = datetime.now().year
        count = db.query(EquipmentLifecycleEvent).count() + 1
        event_number = f"EL-{year}-{count:06d}"

        event = EquipmentLifecycleEvent(
            equipment_id=equipment_id,
            event_number=event_number,
            stage=EquipmentLifecycleStageEnum[stage],
            event_date=datetime.now().date(),
            description=event_data.get("description"),
            performed_by_id=event_data.get("performed_by_id"),
            rfq_id=event_data.get("rfq_id"),
            po_id=event_data.get("po_id"),
            installation_location=event_data.get("installation_location"),
            commissioning_report=event_data.get("commissioning_report"),
            fat_sat_report=event_data.get("fat_sat_report"),
            calibration_id=event_data.get("calibration_id"),
            maintenance_id=event_data.get("maintenance_id"),
            decommission_reason=event_data.get("decommission_reason"),
            cost=event_data.get("cost"),
            documents=event_data.get("documents"),
            metadata=event_data.get("metadata"),
            created_by_id=event_data.get("performed_by_id")
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return {
            "event_id": event.id,
            "event_number": event.event_number,
            "stage": event.stage.value
        }

    finally:
        db.close()
