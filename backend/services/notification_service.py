"""
Notification Service - Centralized notification management
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.notification import Notification
from backend.models.user import User
from backend.services.tasks.notification_tasks import (
    send_email_notification,
    send_in_app_notification,
    send_webhook_notification
)


class NotificationService:
    """
    Centralized notification service

    Supports:
    - Email notifications
    - In-app notifications
    - Webhook notifications
    """

    def __init__(self, db: Session):
        self.db = db

    def notify(
        self,
        user_ids: List[int],
        title: str,
        message: str,
        notification_type: str = "info",
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        send_email: bool = False,
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send notification through multiple channels

        Channels:
        - In-app (always)
        - Email (if send_email=True)
        - Webhook (if webhook_url provided)
        """
        results = {}

        # In-app notification
        send_in_app_notification.delay(
            user_ids=user_ids,
            title=title,
            message=message,
            notification_type=notification_type,
            entity_type=entity_type,
            entity_id=entity_id
        )
        results["in_app"] = True

        # Email notification
        if send_email:
            # Fetch user emails
            users = self.db.query(User).filter(User.id.in_(user_ids)).all()
            emails = [user.email for user in users if user.email]

            if emails:
                send_email_notification.delay(
                    to_emails=emails,
                    subject=title,
                    body=message,
                    html_body=self._generate_html_email(title, message)
                )
                results["email"] = True

        # Webhook notification
        if webhook_url:
            payload = {
                "title": title,
                "message": message,
                "type": notification_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "user_ids": user_ids
            }

            send_webhook_notification.delay(
                webhook_url=webhook_url,
                payload=payload
            )
            results["webhook"] = True

        return results

    def notify_task_assignment(
        self,
        task_id: int,
        task_title: str,
        assigned_to_id: int,
        assigned_by_id: int
    ):
        """Notify user of task assignment"""
        assigned_by = self.db.query(User).get(assigned_by_id)
        assigned_by_name = assigned_by.full_name if assigned_by else "Someone"

        self.notify(
            user_ids=[assigned_to_id],
            title="New Task Assigned",
            message=f"{assigned_by_name} assigned you task: {task_title}",
            notification_type="info",
            entity_type="task",
            entity_id=task_id,
            send_email=True
        )

    def notify_task_status_change(
        self,
        task_id: int,
        task_title: str,
        old_status: str,
        new_status: str,
        watchers: List[int]
    ):
        """Notify watchers of task status change"""
        self.notify(
            user_ids=watchers,
            title="Task Status Updated",
            message=f"Task '{task_title}' status changed from {old_status} to {new_status}",
            notification_type="info",
            entity_type="task",
            entity_id=task_id
        )

    def notify_meeting_scheduled(
        self,
        meeting_id: int,
        meeting_title: str,
        meeting_date: str,
        attendees: List[int]
    ):
        """Notify attendees of scheduled meeting"""
        self.notify(
            user_ids=attendees,
            title="Meeting Scheduled",
            message=f"You've been invited to meeting: {meeting_title} on {meeting_date}",
            notification_type="info",
            entity_type="meeting",
            entity_id=meeting_id,
            send_email=True
        )

    def notify_sla_violation(
        self,
        entity_type: str,
        entity_id: int,
        entity_name: str,
        severity: str,
        assigned_to_id: Optional[int] = None,
        escalate_to_id: Optional[int] = None
    ):
        """Notify of SLA violation"""
        user_ids = []
        if assigned_to_id:
            user_ids.append(assigned_to_id)
        if escalate_to_id:
            user_ids.append(escalate_to_id)

        if user_ids:
            self.notify(
                user_ids=user_ids,
                title=f"SLA Violation - {severity}",
                message=f"{entity_type} '{entity_name}' has violated SLA",
                notification_type="warning",
                entity_type=entity_type,
                entity_id=entity_id,
                send_email=True
            )

    def notify_workflow_step_entered(
        self,
        workflow_instance_id: int,
        workflow_name: str,
        step_name: str,
        assigned_to_id: Optional[int] = None
    ):
        """Notify of workflow step entry"""
        if assigned_to_id:
            self.notify(
                user_ids=[assigned_to_id],
                title="Workflow Action Required",
                message=f"Workflow '{workflow_name}' requires your action at step: {step_name}",
                notification_type="info",
                entity_type="workflow_instance",
                entity_id=workflow_instance_id,
                send_email=True
            )

    def notify_milestone_approaching(
        self,
        milestone_id: int,
        milestone_name: str,
        days_until: int,
        project_manager_id: int,
        team_members: List[int]
    ):
        """Notify of approaching milestone"""
        user_ids = [project_manager_id] + team_members

        self.notify(
            user_ids=user_ids,
            title="Milestone Approaching",
            message=f"Milestone '{milestone_name}' is due in {days_until} days",
            notification_type="warning",
            entity_type="milestone",
            entity_id=milestone_id
        )

    def notify_equipment_calibration_due(
        self,
        equipment_id: int,
        equipment_name: str,
        calibration_date: str,
        custodian_id: Optional[int] = None
    ):
        """Notify of upcoming equipment calibration"""
        if custodian_id:
            self.notify(
                user_ids=[custodian_id],
                title="Equipment Calibration Due",
                message=f"Equipment '{equipment_name}' calibration due on {calibration_date}",
                notification_type="warning",
                entity_type="equipment",
                entity_id=equipment_id,
                send_email=True
            )

    def _generate_html_email(self, title: str, message: str) -> str:
        """Generate HTML email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ padding: 10px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{title}</h2>
                </div>
                <div class="content">
                    <p>{message}</p>
                </div>
                <div class="footer">
                    <p>LIMS-QMS Organization OS</p>
                    <p>This is an automated notification. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
