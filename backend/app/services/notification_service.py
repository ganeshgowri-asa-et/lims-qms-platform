"""
Notification service for email and SMS alerts
"""
from typing import List, Optional
from datetime import date
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from twilio.rest import Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications"""

    @staticmethod
    def get_mail_config() -> ConnectionConfig:
        """Get email configuration"""
        return ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=settings.MAIL_TLS,
            MAIL_SSL_TLS=settings.MAIL_SSL,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )

    @staticmethod
    async def send_email(
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ):
        """Send email notification"""
        try:
            conf = EmailService.get_mail_config()
            message = MessageSchema(
                subject=subject,
                recipients=to_emails,
                body=html_body if html_body else body,
                subtype="html" if html_body else "plain",
            )

            fm = FastMail(conf)
            await fm.send_message(message)
            logger.info(f"Email sent successfully to {to_emails}")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise

    @staticmethod
    async def send_calibration_due_alert(
        to_emails: List[str],
        equipment_name: str,
        equipment_id: str,
        due_date: date,
        days_until_due: int,
    ):
        """Send calibration due date alert email"""
        subject = f"Calibration Due Alert: {equipment_name}"

        if days_until_due < 0:
            urgency = "OVERDUE"
            urgency_class = "overdue"
        elif days_until_due <= 7:
            urgency = "URGENT - 7 Days"
            urgency_class = "urgent"
        elif days_until_due <= 15:
            urgency = "Important - 15 Days"
            urgency_class = "important"
        else:
            urgency = "Notice - 30 Days"
            urgency_class = "notice"

        html_body = f"""
        <html>
        <head>
            <style>
                .email-container {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #003366;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .content {{
                    padding: 20px;
                    background-color: #f9f9f9;
                    border: 1px solid #ddd;
                }}
                .alert-box {{
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 5px;
                }}
                .overdue {{
                    background-color: #ffebee;
                    border-left: 5px solid #d32f2f;
                }}
                .urgent {{
                    background-color: #fff3e0;
                    border-left: 5px solid #f57c00;
                }}
                .important {{
                    background-color: #fff9c4;
                    border-left: 5px solid #fbc02d;
                }}
                .notice {{
                    background-color: #e3f2fd;
                    border-left: 5px solid #1976d2;
                }}
                .details {{
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>Calibration Due Alert</h1>
                </div>
                <div class="content">
                    <div class="alert-box {urgency_class}">
                        <h2>⚠️ {urgency}</h2>
                        <p><strong>Equipment:</strong> {equipment_name} ({equipment_id})</p>
                        <p><strong>Due Date:</strong> {due_date.strftime('%Y-%m-%d')}</p>
                        <p><strong>Days Until Due:</strong> {days_until_due} days</p>
                    </div>
                    <div class="details">
                        <h3>Action Required:</h3>
                        <p>Please arrange for calibration of this equipment as soon as possible to maintain compliance and ensure accurate measurements.</p>
                        <ol>
                            <li>Review the equipment calibration schedule</li>
                            <li>Contact approved calibration vendor</li>
                            <li>Schedule calibration appointment</li>
                            <li>Update calibration records in LIMS-QMS system</li>
                        </ol>
                    </div>
                </div>
                <div class="footer">
                    <p>This is an automated notification from the LIMS-QMS Platform.</p>
                    <p>Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        await EmailService.send_email(to_emails, subject, "", html_body)


class SMSService:
    """Service for sending SMS notifications"""

    @staticmethod
    def get_twilio_client() -> Optional[Client]:
        """Get Twilio client"""
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            logger.warning("Twilio credentials not configured")
            return None

        return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    @staticmethod
    def send_sms(to_phone: str, message: str):
        """Send SMS notification"""
        try:
            client = SMSService.get_twilio_client()
            if not client:
                logger.warning("SMS service not configured, skipping SMS")
                return

            message_obj = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_phone,
            )

            logger.info(f"SMS sent successfully to {to_phone}, SID: {message_obj.sid}")
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            # Don't raise exception for SMS failures

    @staticmethod
    def send_calibration_due_sms(
        to_phone: str,
        equipment_name: str,
        equipment_id: str,
        days_until_due: int,
    ):
        """Send calibration due SMS alert"""
        if days_until_due < 0:
            urgency = "OVERDUE"
        elif days_until_due <= 7:
            urgency = "URGENT"
        else:
            urgency = "DUE SOON"

        message = f"[LIMS-QMS] {urgency}: Calibration due for {equipment_name} ({equipment_id}) in {days_until_due} days. Please schedule calibration."

        SMSService.send_sms(to_phone, message)


class NotificationService:
    """Combined notification service"""

    @staticmethod
    async def send_calibration_alert(
        email_addresses: List[str],
        phone_numbers: List[str],
        equipment_name: str,
        equipment_id: str,
        due_date: date,
        days_until_due: int,
    ):
        """Send calibration alert via email and SMS"""
        # Send email
        if email_addresses:
            await EmailService.send_calibration_due_alert(
                email_addresses,
                equipment_name,
                equipment_id,
                due_date,
                days_until_due,
            )

        # Send SMS
        if phone_numbers:
            for phone in phone_numbers:
                SMSService.send_calibration_due_sms(
                    phone, equipment_name, equipment_id, days_until_due
                )
