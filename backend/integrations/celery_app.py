"""
Celery Configuration for Async Task Processing
Handles background jobs, scheduled tasks, and distributed processing
"""
from celery import Celery
from celery.schedules import crontab
from backend.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "lims_qms",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'backend.integrations.tasks.notifications',
        'backend.integrations.tasks.backups',
        'backend.integrations.tasks.etl',
        'backend.integrations.tasks.monitoring',
        'backend.integrations.tasks.ai_tasks',
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    # Backup tasks
    'database-backup-daily': {
        'task': 'backend.integrations.tasks.backups.backup_database',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'file-backup-daily': {
        'task': 'backend.integrations.tasks.backups.backup_files',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },

    # Monitoring tasks
    'health-check-every-5-minutes': {
        'task': 'backend.integrations.tasks.monitoring.system_health_check',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'performance-metrics-hourly': {
        'task': 'backend.integrations.tasks.monitoring.collect_performance_metrics',
        'schedule': crontab(minute=0),  # Every hour
    },

    # Notification tasks
    'send-daily-digest': {
        'task': 'backend.integrations.tasks.notifications.send_daily_digest',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    'check-overdue-tasks': {
        'task': 'backend.integrations.tasks.notifications.check_overdue_tasks',
        'schedule': crontab(hour='*/4', minute=0),  # Every 4 hours
    },

    # ETL tasks
    'sync-external-data': {
        'task': 'backend.integrations.tasks.etl.sync_external_systems',
        'schedule': crontab(hour='*/6', minute=0),  # Every 6 hours
    },
    'cleanup-old-data': {
        'task': 'backend.integrations.tasks.etl.cleanup_old_data',
        'schedule': crontab(hour=1, minute=0, day_of_week=0),  # Weekly on Sunday at 1 AM
    },

    # AI tasks
    'process-pending-ai-requests': {
        'task': 'backend.integrations.tasks.ai_tasks.process_pending_requests',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
    },
}

logger.info("Celery app configured successfully")
