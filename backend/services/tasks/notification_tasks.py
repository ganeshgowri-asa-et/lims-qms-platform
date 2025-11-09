"""
Notification-related Celery tasks
"""
from backend.services.celery_app import celery_app
from backend.core.database import SessionLocal
from typing import Dict, Any, List
import json


@celery_app.task(name="backend.services.tasks.notification_tasks.send_email_notification")
def send_email_notification(
    to_emails: List[str],
    subject: str,
    body: str,
    html_body: str = None
):
    """
    Send email notification
    """
    # This would integrate with FastAPI-Mail or similar
    # For now, just log
    print(f"Sending email to {to_emails}: {subject}")

    return {
        "sent": True,
        "recipients": len(to_emails)
    }


@celery_app.task(name="backend.services.tasks.notification_tasks.send_in_app_notification")
def send_in_app_notification(
    user_ids: List[int],
    title: str,
    message: str,
    notification_type: str = "info",
    entity_type: str = None,
    entity_id: int = None
):
    """
    Send in-app notification
    """
    from backend.models.notification import Notification

    db = SessionLocal()
    try:
        notifications = []

        for user_id in user_ids:
            notif = Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                entity_type=entity_type,
                entity_id=entity_id,
                is_read=False,
                created_by_id=user_id
            )
            db.add(notif)
            notifications.append(notif)

        db.commit()

        return {
            "sent": True,
            "count": len(notifications)
        }

    finally:
        db.close()


@celery_app.task(name="backend.services.tasks.notification_tasks.send_webhook_notification")
def send_webhook_notification(
    webhook_url: str,
    payload: Dict[str, Any]
):
    """
    Send webhook notification
    """
    import httpx

    try:
        response = httpx.post(
            webhook_url,
            json=payload,
            timeout=10
        )

        return {
            "sent": True,
            "status_code": response.status_code
        }

    except Exception as e:
        return {
            "sent": False,
            "error": str(e)
        }


@celery_app.task(name="backend.services.tasks.notification_tasks.send_task_reminders")
def send_task_reminders():
    """
    Send reminders for upcoming task deadlines
    """
    from backend.models.workflow import Task, TaskStatusEnum
    from datetime import datetime, timedelta

    db = SessionLocal()
    try:
        # Tasks due in next 24 hours
        tomorrow = (datetime.now() + timedelta(days=1)).date()

        upcoming_tasks = db.query(Task).filter(
            Task.status.in_([TaskStatusEnum.TODO, TaskStatusEnum.IN_PROGRESS]),
            Task.due_date == tomorrow,
            Task.is_deleted == False,
            Task.assigned_to_id.isnot(None)
        ).all()

        reminders_sent = 0
        for task in upcoming_tasks:
            # Send notification
            send_in_app_notification.delay(
                user_ids=[task.assigned_to_id],
                title="Task Reminder",
                message=f"Task '{task.title}' is due tomorrow ({task.due_date})",
                notification_type="warning",
                entity_type="task",
                entity_id=task.id
            )
            reminders_sent += 1

        return {
            "tasks_checked": len(upcoming_tasks),
            "reminders_sent": reminders_sent
        }

    finally:
        db.close()


@celery_app.task(name="backend.services.tasks.notification_tasks.send_meeting_reminders")
def send_meeting_reminders():
    """
    Send reminders for upcoming meetings
    """
    from backend.models.workflow import Meeting
    from datetime import datetime, timedelta

    db = SessionLocal()
    try:
        # Meetings in next 2 hours
        now = datetime.now()
        two_hours_later = now + timedelta(hours=2)

        # Get today's date
        today = now.date()

        upcoming_meetings = db.query(Meeting).filter(
            Meeting.meeting_date == today,
            Meeting.is_deleted == False
        ).all()

        reminders_sent = 0
        for meeting in upcoming_meetings:
            # Parse start time and check if within 2 hours
            # Simplified - in production would parse time properly

            attendees = meeting.attendees or []
            if attendees and isinstance(attendees, list):
                # Send to all attendees
                send_in_app_notification.delay(
                    user_ids=attendees,
                    title="Meeting Reminder",
                    message=f"Meeting '{meeting.title}' today at {meeting.start_time or 'TBD'}",
                    notification_type="info",
                    entity_type="meeting",
                    entity_id=meeting.id
                )
                reminders_sent += 1

        return {
            "meetings_checked": len(upcoming_meetings),
            "reminders_sent": reminders_sent
        }

    finally:
        db.close()
