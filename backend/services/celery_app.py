"""
Celery application configuration
"""
from celery import Celery
from backend.core.config import settings

celery_app = Celery(
    "lims_qms",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "backend.services.tasks.workflow_tasks",
        "backend.services.tasks.notification_tasks",
        "backend.services.tasks.sla_tasks",
        "backend.services.tasks.calendar_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks configuration
celery_app.conf.beat_schedule = {
    "check-sla-violations": {
        "task": "backend.services.tasks.sla_tasks.check_sla_violations",
        "schedule": 300.0,  # Every 5 minutes
    },
    "send-task-reminders": {
        "task": "backend.services.tasks.notification_tasks.send_task_reminders",
        "schedule": 3600.0,  # Every hour
    },
    "send-meeting-reminders": {
        "task": "backend.services.tasks.notification_tasks.send_meeting_reminders",
        "schedule": 1800.0,  # Every 30 minutes
    },
    "update-calibration-schedules": {
        "task": "backend.services.tasks.workflow_tasks.update_calibration_schedules",
        "schedule": 86400.0,  # Daily
    },
}
