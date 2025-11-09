"""
Notification Tasks
Background tasks for sending notifications, digests, reminders
"""
from backend.integrations.celery_app import celery_app
from backend.integrations.notifications import notification_hub, NotificationChannel
from backend.integrations.events import event_bus, Event, EventType
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="backend.integrations.tasks.notifications.send_notification")
def send_notification_task(
    user_id: int,
    title: str,
    message: str,
    channels: list,
    priority: str = "normal"
):
    """
    Async task to send notification

    Args:
        user_id: User ID
        title: Notification title
        message: Notification message
        channels: List of channels
        priority: Priority level
    """
    import asyncio

    channel_enums = [NotificationChannel(c) for c in channels]

    result = asyncio.run(notification_hub.send_notification(
        user_id=user_id,
        title=title,
        message=message,
        channels=channel_enums,
        priority=priority
    ))

    logger.info(f"Notification sent to user {user_id}: {result}")
    return result


@celery_app.task(name="backend.integrations.tasks.notifications.send_daily_digest")
def send_daily_digest():
    """
    Send daily digest to all users
    Runs daily at 9 AM
    """
    import asyncio

    logger.info("Starting daily digest task")

    # Get all active users
    # Placeholder - would query database
    active_users = [1, 2, 3]  # Example user IDs

    sent_count = 0
    for user_id in active_users:
        try:
            result = asyncio.run(notification_hub.send_digest(
                user_id=user_id,
                digest_type="daily"
            ))

            if result:
                sent_count += 1

        except Exception as e:
            logger.error(f"Failed to send digest to user {user_id}: {e}")

    logger.info(f"Daily digest sent to {sent_count}/{len(active_users)} users")
    return {"sent": sent_count, "total": len(active_users)}


@celery_app.task(name="backend.integrations.tasks.notifications.check_overdue_tasks")
def check_overdue_tasks():
    """
    Check for overdue tasks and send reminders
    Runs every 4 hours
    """
    import asyncio

    logger.info("Checking for overdue tasks")

    # Query database for overdue tasks
    # Placeholder
    overdue_tasks = []

    for task in overdue_tasks:
        try:
            # Send notification
            asyncio.run(notification_hub.send_notification(
                user_id=task['assigned_to'],
                title="Task Overdue",
                message=f"Task '{task['title']}' is overdue by {task['days_overdue']} days",
                channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                priority="high"
            ))

            # Publish event
            asyncio.run(event_bus.publish(Event(
                type=EventType.TASK_OVERDUE,
                source="task_checker",
                data={'task_id': task['id']},
                user_id=task['assigned_to']
            )))

        except Exception as e:
            logger.error(f"Failed to send overdue notification for task {task['id']}: {e}")

    logger.info(f"Processed {len(overdue_tasks)} overdue tasks")
    return {"overdue_tasks": len(overdue_tasks)}


@celery_app.task(name="backend.integrations.tasks.notifications.send_training_reminders")
def send_training_reminders():
    """
    Send training due reminders
    Runs daily
    """
    import asyncio

    logger.info("Checking for training due dates")

    # Query database for training due soon
    # Placeholder
    upcoming_training = []

    for training in upcoming_training:
        try:
            asyncio.run(notification_hub.send_notification(
                user_id=training['employee_id'],
                title="Training Due Soon",
                message=f"Training '{training['name']}' is due on {training['due_date']}",
                channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                priority="normal"
            ))

        except Exception as e:
            logger.error(f"Failed to send training reminder: {e}")

    logger.info(f"Sent {len(upcoming_training)} training reminders")
    return {"reminders_sent": len(upcoming_training)}


@celery_app.task(name="backend.integrations.tasks.notifications.send_bulk_notification")
def send_bulk_notification(
    user_ids: list,
    title: str,
    message: str,
    channels: list
):
    """
    Send notification to multiple users

    Args:
        user_ids: List of user IDs
        title: Notification title
        message: Notification message
        channels: List of channels
    """
    import asyncio

    channel_enums = [NotificationChannel(c) for c in channels]
    sent_count = 0

    for user_id in user_ids:
        try:
            result = asyncio.run(notification_hub.send_notification(
                user_id=user_id,
                title=title,
                message=message,
                channels=channel_enums
            ))

            if any(result.values()):
                sent_count += 1

        except Exception as e:
            logger.error(f"Failed to send notification to user {user_id}: {e}")

    logger.info(f"Bulk notification sent to {sent_count}/{len(user_ids)} users")
    return {"sent": sent_count, "total": len(user_ids)}
