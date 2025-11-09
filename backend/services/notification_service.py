"""
Notification Service - Email and in-app notifications for workflow events
"""
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import Notification, User, FormRecord, FormTemplate
from backend.core.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class NotificationService:
    """Service for sending notifications"""

    def __init__(self, db: Session):
        self.db = db

    def notify_submission(self, record_id: int) -> None:
        """Notify checker when record is submitted"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record or not record.checker_id:
            return

        template = self.db.query(FormTemplate).filter_by(id=record.template_id).first()
        doer = self.db.query(User).filter_by(id=record.doer_id).first()

        # Create in-app notification
        notification = Notification(
            user_id=record.checker_id,
            title="New Form Submission for Review",
            message=f"Record {record.record_number} has been submitted by {doer.full_name if doer else 'Unknown'} and requires your review.",
            notification_type="info",
            category="approval",
            link=f"/forms/records/{record.id}",
            metadata={
                "record_id": record.id,
                "record_number": record.record_number,
                "template_name": template.name if template else None,
                "action_required": "review"
            },
            priority="high"
        )
        self.db.add(notification)
        self.db.commit()

        # Send email notification
        checker = self.db.query(User).filter_by(id=record.checker_id).first()
        if checker and checker.email:
            subject = f"Form Submission for Review: {record.record_number}"
            body = f"""
Dear {checker.full_name},

A new form record has been submitted and requires your review:

Record Number: {record.record_number}
Title: {record.title or 'N/A'}
Template: {template.name if template else 'N/A'}
Submitted By: {doer.full_name if doer else 'Unknown'}
Submitted At: {record.submitted_at}

Please review this record at your earliest convenience.

Link: {settings.API_BASE_URL}/forms/records/{record.id}

Best regards,
LIMS-QMS System
            """
            self._send_email(checker.email, subject, body)

    def notify_review_complete(self, record_id: int, approved: bool) -> None:
        """Notify doer and approver when checker reviews"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record:
            return

        template = self.db.query(FormTemplate).filter_by(id=record.template_id).first()
        checker = self.db.query(User).filter_by(id=record.checker_id).first()

        if approved and record.approver_id:
            # Notify approver
            notification = Notification(
                user_id=record.approver_id,
                title="Form Record Ready for Approval",
                message=f"Record {record.record_number} has been reviewed and is ready for your approval.",
                notification_type="info",
                category="approval",
                link=f"/forms/records/{record.id}",
                metadata={
                    "record_id": record.id,
                    "record_number": record.record_number,
                    "template_name": template.name if template else None,
                    "action_required": "approve"
                },
                priority="high"
            )
            self.db.add(notification)

            approver = self.db.query(User).filter_by(id=record.approver_id).first()
            if approver and approver.email:
                subject = f"Form Record for Approval: {record.record_number}"
                body = f"""
Dear {approver.full_name},

A form record has been reviewed and is ready for your approval:

Record Number: {record.record_number}
Title: {record.title or 'N/A'}
Template: {template.name if template else 'N/A'}
Reviewed By: {checker.full_name if checker else 'Unknown'}
Reviewed At: {record.checked_at}

Please review and approve this record.

Link: {settings.API_BASE_URL}/forms/records/{record.id}

Best regards,
LIMS-QMS System
                """
                self._send_email(approver.email, subject, body)

        elif not approved and record.doer_id:
            # Notify doer about revision request
            notification = Notification(
                user_id=record.doer_id,
                title="Revision Required",
                message=f"Record {record.record_number} requires revision. Comments: {record.checker_comments}",
                notification_type="warning",
                category="approval",
                link=f"/forms/records/{record.id}",
                metadata={
                    "record_id": record.id,
                    "record_number": record.record_number,
                    "template_name": template.name if template else None,
                    "action_required": "revise"
                },
                priority="high"
            )
            self.db.add(notification)

            doer = self.db.query(User).filter_by(id=record.doer_id).first()
            if doer and doer.email:
                subject = f"Revision Required: {record.record_number}"
                body = f"""
Dear {doer.full_name},

Your form record requires revision:

Record Number: {record.record_number}
Title: {record.title or 'N/A'}
Template: {template.name if template else 'N/A'}
Reviewed By: {checker.full_name if checker else 'Unknown'}

Comments:
{record.checker_comments or 'No comments provided'}

Please revise and resubmit the record.

Link: {settings.API_BASE_URL}/forms/records/{record.id}

Best regards,
LIMS-QMS System
                """
                self._send_email(doer.email, subject, body)

        self.db.commit()

    def notify_approval(self, record_id: int, approved: bool) -> None:
        """Notify doer when record is approved or rejected"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record or not record.doer_id:
            return

        template = self.db.query(FormTemplate).filter_by(id=record.template_id).first()
        approver = self.db.query(User).filter_by(id=record.approver_id).first()
        doer = self.db.query(User).filter_by(id=record.doer_id).first()

        if approved:
            # Notify doer of approval
            notification = Notification(
                user_id=record.doer_id,
                title="Form Record Approved",
                message=f"Record {record.record_number} has been approved!",
                notification_type="success",
                category="approval",
                link=f"/forms/records/{record.id}",
                metadata={
                    "record_id": record.id,
                    "record_number": record.record_number,
                    "template_name": template.name if template else None
                },
                priority="normal"
            )
            self.db.add(notification)

            if doer and doer.email:
                subject = f"Form Record Approved: {record.record_number}"
                body = f"""
Dear {doer.full_name},

Congratulations! Your form record has been approved:

Record Number: {record.record_number}
Title: {record.title or 'N/A'}
Template: {template.name if template else 'N/A'}
Approved By: {approver.full_name if approver else 'Unknown'}
Approved At: {record.approved_at}

Link: {settings.API_BASE_URL}/forms/records/{record.id}

Best regards,
LIMS-QMS System
                """
                self._send_email(doer.email, subject, body)

        else:
            # Notify doer of rejection
            notification = Notification(
                user_id=record.doer_id,
                title="Form Record Rejected",
                message=f"Record {record.record_number} has been rejected. Reason: {record.rejection_reason}",
                notification_type="error",
                category="approval",
                link=f"/forms/records/{record.id}",
                metadata={
                    "record_id": record.id,
                    "record_number": record.record_number,
                    "template_name": template.name if template else None
                },
                priority="high"
            )
            self.db.add(notification)

            if doer and doer.email:
                subject = f"Form Record Rejected: {record.record_number}"
                body = f"""
Dear {doer.full_name},

Your form record has been rejected:

Record Number: {record.record_number}
Title: {record.title or 'N/A'}
Template: {template.name if template else 'N/A'}
Rejected By: {approver.full_name if approver else 'Unknown'}
Rejected At: {record.rejected_at}

Reason:
{record.rejection_reason or 'No reason provided'}

Link: {settings.API_BASE_URL}/forms/records/{record.id}

Best regards,
LIMS-QMS System
                """
                self._send_email(doer.email, subject, body)

        self.db.commit()

    def notify_comment(
        self,
        record_id: int,
        commenter_id: int,
        comment_content: str,
        mentioned_users: Optional[List[int]] = None
    ) -> None:
        """Notify users about new comments"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record:
            return

        commenter = self.db.query(User).filter_by(id=commenter_id).first()
        template = self.db.query(FormTemplate).filter_by(id=record.template_id).first()

        # Notify record stakeholders (doer, checker, approver)
        stakeholder_ids = [
            record.doer_id,
            record.checker_id,
            record.approver_id
        ]
        stakeholder_ids = [uid for uid in stakeholder_ids if uid and uid != commenter_id]

        # Add mentioned users
        if mentioned_users:
            stakeholder_ids.extend([uid for uid in mentioned_users if uid not in stakeholder_ids])

        for user_id in stakeholder_ids:
            notification = Notification(
                user_id=user_id,
                title="New Comment on Form Record",
                message=f"{commenter.full_name if commenter else 'Someone'} commented on record {record.record_number}",
                notification_type="info",
                category="task",
                link=f"/forms/records/{record.id}#comments",
                metadata={
                    "record_id": record.id,
                    "record_number": record.record_number,
                    "template_name": template.name if template else None,
                    "comment": comment_content[:100]
                },
                priority="normal"
            )
            self.db.add(notification)

        self.db.commit()

    def notify_due_date_approaching(self, record_id: int) -> None:
        """Notify when record due date is approaching"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record or not record.due_date:
            return

        template = self.db.query(FormTemplate).filter_by(id=record.template_id).first()

        # Determine who to notify based on current status
        user_id = None
        role = None

        if record.status.value == "draft" or record.status.value == "revision_required":
            user_id = record.doer_id
            role = "doer"
        elif record.status.value == "submitted":
            user_id = record.checker_id
            role = "checker"
        elif record.status.value == "under_review":
            user_id = record.approver_id
            role = "approver"

        if not user_id:
            return

        notification = Notification(
            user_id=user_id,
            title="Form Record Due Date Approaching",
            message=f"Record {record.record_number} is due soon: {record.due_date}",
            notification_type="warning",
            category="task",
            link=f"/forms/records/{record.id}",
            metadata={
                "record_id": record.id,
                "record_number": record.record_number,
                "template_name": template.name if template else None,
                "due_date": record.due_date,
                "role": role
            },
            priority="high"
        )
        self.db.add(notification)
        self.db.commit()

    def notify_bulk_upload_complete(
        self,
        user_id: int,
        upload_id: int,
        success: bool,
        total_rows: int,
        successful_rows: int,
        failed_rows: int
    ) -> None:
        """Notify user when bulk upload is complete"""
        notification_type = "success" if success else "warning"

        message = f"Bulk upload completed: {successful_rows}/{total_rows} records created successfully"
        if failed_rows > 0:
            message += f", {failed_rows} failed"

        notification = Notification(
            user_id=user_id,
            title="Bulk Upload Complete",
            message=message,
            notification_type=notification_type,
            category="task",
            link=f"/forms/bulk-uploads/{upload_id}",
            metadata={
                "upload_id": upload_id,
                "total_rows": total_rows,
                "successful_rows": successful_rows,
                "failed_rows": failed_rows
            },
            priority="normal"
        )
        self.db.add(notification)
        self.db.commit()

    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email notification"""
        try:
            # Check if SMTP is configured
            if not settings.SMTP_HOST or not settings.SMTP_USER:
                print(f"SMTP not configured. Email not sent to {to_email}")
                return False

            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_USER
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()

            return True
        except Exception as e:
            print(f"Error sending email to {to_email}: {str(e)}")
            return False

    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict]:
        """Get notifications for a user"""
        query = self.db.query(Notification).filter_by(user_id=user_id)

        if unread_only:
            query = query.filter_by(is_read=False)

        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()

        result = []
        for notification in notifications:
            result.append({
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "category": notification.category,
                "is_read": notification.is_read,
                "read_at": notification.read_at,
                "link": notification.link,
                "metadata": notification.metadata,
                "priority": notification.priority,
                "created_at": notification.created_at
            })

        return result

    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark notification as read"""
        notification = self.db.query(Notification).filter_by(
            id=notification_id,
            user_id=user_id
        ).first()

        if not notification:
            return False

        notification.is_read = True
        notification.read_at = datetime.utcnow().isoformat()
        self.db.commit()

        return True

    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        count = self.db.query(Notification).filter_by(
            user_id=user_id,
            is_read=False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow().isoformat()
        })
        self.db.commit()

        return count

    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        return self.db.query(Notification).filter_by(
            user_id=user_id,
            is_read=False
        ).count()
