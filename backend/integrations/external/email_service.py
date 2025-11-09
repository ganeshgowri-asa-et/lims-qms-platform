"""
Email Service Integration
SMTP for outgoing, IMAP for incoming emails
"""
from typing import List, Dict, Optional, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import imaplib
import email
from datetime import datetime
from jinja2 import Template
from backend.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending and receiving emails"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM

    async def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        html: bool = False,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Send email

        Args:
            to: List of recipient emails
            subject: Email subject
            body: Email body
            html: Whether body is HTML
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachments

        Returns:
            Success status
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to)
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = ', '.join(cc)

            # Add body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # Add attachments
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)

                # Combine all recipients
                all_recipients = to + (cc or []) + (bcc or [])
                server.send_message(msg, to_addrs=all_recipients)

            logger.info(f"Email sent to {', '.join(to)}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email"""
        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment['content'])
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={attachment["filename"]}'
            )
            msg.attach(part)
        except Exception as e:
            logger.error(f"Failed to add attachment: {e}")

    async def send_template_email(
        self,
        to: List[str],
        template_name: str,
        template_data: Dict[str, Any],
        subject: str
    ) -> bool:
        """
        Send email using template

        Args:
            to: List of recipient emails
            template_name: Template name
            template_data: Data for template
            subject: Email subject

        Returns:
            Success status
        """
        try:
            # Load template
            template = self._load_template(template_name)

            # Render template
            body = template.render(**template_data)

            # Send email
            return await self.send_email(to, subject, body, html=True)

        except Exception as e:
            logger.error(f"Failed to send template email: {e}")
            return False

    def _load_template(self, template_name: str) -> Template:
        """Load email template"""
        # In production, load from file or database
        templates = {
            'task_assigned': '''
                <html>
                <body>
                    <h2>New Task Assigned</h2>
                    <p>Hi {{ user_name }},</p>
                    <p>You have been assigned a new task:</p>
                    <ul>
                        <li><strong>Task:</strong> {{ task_title }}</li>
                        <li><strong>Due Date:</strong> {{ due_date }}</li>
                        <li><strong>Priority:</strong> {{ priority }}</li>
                    </ul>
                    <p><a href="{{ task_url }}">View Task</a></p>
                </body>
                </html>
            ''',
            'document_approval': '''
                <html>
                <body>
                    <h2>Document Requires Your Approval</h2>
                    <p>Hi {{ user_name }},</p>
                    <p>A document requires your approval:</p>
                    <ul>
                        <li><strong>Document:</strong> {{ document_title }}</li>
                        <li><strong>Type:</strong> {{ document_type }}</li>
                        <li><strong>Submitted By:</strong> {{ submitted_by }}</li>
                    </ul>
                    <p><a href="{{ approval_url }}">Review and Approve</a></p>
                </body>
                </html>
            ''',
            'daily_digest': '''
                <html>
                <body>
                    <h2>Daily Digest - {{ date }}</h2>
                    <p>Hi {{ user_name }},</p>

                    <h3>Tasks ({{ tasks_count }})</h3>
                    <ul>
                    {% for task in tasks %}
                        <li>{{ task.title }} - Due: {{ task.due_date }}</li>
                    {% endfor %}
                    </ul>

                    <h3>Pending Approvals ({{ approvals_count }})</h3>
                    <ul>
                    {% for approval in approvals %}
                        <li>{{ approval.title }} - {{ approval.type }}</li>
                    {% endfor %}
                    </ul>

                    <p><a href="{{ dashboard_url }}">View Dashboard</a></p>
                </body>
                </html>
            '''
        }

        template_str = templates.get(template_name, '<p>{{ message }}</p>')
        return Template(template_str)

    async def fetch_inbox(
        self,
        folder: str = "INBOX",
        limit: int = 100,
        unread_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch emails from inbox

        Args:
            folder: Email folder
            limit: Max emails to fetch
            unread_only: Fetch only unread emails

        Returns:
            List of emails
        """
        try:
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(self.smtp_host)
            mail.login(self.smtp_user, self.smtp_password)
            mail.select(folder)

            # Search for emails
            if unread_only:
                _, message_numbers = mail.search(None, 'UNSEEN')
            else:
                _, message_numbers = mail.search(None, 'ALL')

            emails = []
            for num in message_numbers[0].split()[:limit]:
                _, msg_data = mail.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                emails.append({
                    'id': num.decode(),
                    'from': email_message['From'],
                    'to': email_message['To'],
                    'subject': email_message['Subject'],
                    'date': email_message['Date'],
                    'body': self._extract_email_body(email_message)
                })

            mail.close()
            mail.logout()

            logger.info(f"Fetched {len(emails)} emails from {folder}")
            return emails

        except Exception as e:
            logger.error(f"Failed to fetch emails: {e}")
            return []

    def _extract_email_body(self, email_message) -> str:
        """Extract email body"""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return email_message.get_payload(decode=True).decode()


# Global email service instance
email_service = EmailService()
