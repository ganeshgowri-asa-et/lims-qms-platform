"""
Multi-Channel Notification Hub
Email, In-app, SMS, Webhooks, Slack/Teams integration
"""
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
from backend.integrations.external.email_service import email_service
from backend.integrations.events import event_bus, Event, EventType
from backend.core.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    """Notification channels"""
    EMAIL = "email"
    IN_APP = "in_app"
    SMS = "sms"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationHub:
    """
    Central notification hub
    Manages all outgoing notifications across multiple channels
    """

    def __init__(self):
        self.twilio_account_sid: Optional[str] = None
        self.twilio_auth_token: Optional[str] = None
        self.twilio_phone: Optional[str] = None
        self.slack_webhook_url: Optional[str] = None
        self.teams_webhook_url: Optional[str] = None

    async def send_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        channels: List[NotificationChannel],
        priority: NotificationPriority = NotificationPriority.NORMAL,
        data: Optional[Dict[str, Any]] = None,
        action_url: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Send notification through multiple channels

        Args:
            user_id: Target user ID
            title: Notification title
            message: Notification message
            channels: List of channels to use
            priority: Notification priority
            data: Additional data
            action_url: URL for action button

        Returns:
            Status for each channel
        """
        results = {}

        # Send through each channel
        for channel in channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    results[channel.value] = await self._send_email(
                        user_id, title, message, data
                    )
                elif channel == NotificationChannel.IN_APP:
                    results[channel.value] = await self._send_in_app(
                        user_id, title, message, priority, action_url
                    )
                elif channel == NotificationChannel.SMS:
                    results[channel.value] = await self._send_sms(
                        user_id, message
                    )
                elif channel == NotificationChannel.WEBHOOK:
                    results[channel.value] = await self._send_webhook(
                        title, message, data
                    )
                elif channel == NotificationChannel.SLACK:
                    results[channel.value] = await self._send_slack(
                        title, message, data
                    )
                elif channel == NotificationChannel.TEAMS:
                    results[channel.value] = await self._send_teams(
                        title, message, data
                    )

            except Exception as e:
                logger.error(f"Failed to send {channel.value} notification: {e}")
                results[channel.value] = False

        # Publish event
        await event_bus.publish(Event(
            type=EventType.NOTIFICATION_SENT,
            source="notification_hub",
            data={
                'user_id': user_id,
                'title': title,
                'channels': [c.value for c in channels],
                'priority': priority.value,
                'success': any(results.values())
            },
            user_id=user_id
        ))

        return results

    async def _send_email(
        self,
        user_id: int,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]]
    ) -> bool:
        """Send email notification"""
        try:
            # Get user email from database
            # For now, use placeholder
            user_email = f"user{user_id}@example.com"

            return await email_service.send_email(
                to=[user_email],
                subject=title,
                body=message,
                html=True
            )

        except Exception as e:
            logger.error(f"Email notification error: {e}")
            return False

    async def _send_in_app(
        self,
        user_id: int,
        title: str,
        message: str,
        priority: NotificationPriority,
        action_url: Optional[str]
    ) -> bool:
        """Send in-app notification"""
        try:
            # Store notification in database
            # This would typically use SQLAlchemy model
            notification_data = {
                'user_id': user_id,
                'title': title,
                'message': message,
                'priority': priority.value,
                'action_url': action_url,
                'read': False,
                'created_at': datetime.utcnow()
            }

            # Publish to Redis for real-time updates
            await event_bus.publish(Event(
                type=EventType.NOTIFICATION_SENT,
                source="in_app",
                data=notification_data,
                user_id=user_id
            ))

            logger.info(f"In-app notification sent to user {user_id}")
            return True

        except Exception as e:
            logger.error(f"In-app notification error: {e}")
            return False

    async def _send_sms(self, user_id: int, message: str) -> bool:
        """Send SMS notification via Twilio"""
        try:
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone]):
                logger.warning("Twilio not configured")
                return False

            # Get user phone from database
            user_phone = f"+1234567890"  # Placeholder

            # Send SMS using Twilio API
            async with httpx.AsyncClient() as client:
                auth = (self.twilio_account_sid, self.twilio_auth_token)
                data = {
                    'From': self.twilio_phone,
                    'To': user_phone,
                    'Body': message
                }

                response = await client.post(
                    f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json",
                    auth=auth,
                    data=data
                )

                if response.status_code == 201:
                    logger.info(f"SMS sent to user {user_id}")
                    return True

            return False

        except Exception as e:
            logger.error(f"SMS notification error: {e}")
            return False

    async def _send_webhook(
        self,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]]
    ) -> bool:
        """Send webhook notification"""
        try:
            webhook_url = data.get('webhook_url') if data else None
            if not webhook_url:
                return False

            async with httpx.AsyncClient() as client:
                payload = {
                    'title': title,
                    'message': message,
                    'timestamp': datetime.utcnow().isoformat(),
                    'data': data
                }

                response = await client.post(webhook_url, json=payload)
                return response.status_code == 200

        except Exception as e:
            logger.error(f"Webhook notification error: {e}")
            return False

    async def _send_slack(
        self,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]]
    ) -> bool:
        """Send Slack notification"""
        try:
            if not self.slack_webhook_url:
                logger.warning("Slack webhook not configured")
                return False

            async with httpx.AsyncClient() as client:
                payload = {
                    'text': title,
                    'blocks': [
                        {
                            'type': 'header',
                            'text': {'type': 'plain_text', 'text': title}
                        },
                        {
                            'type': 'section',
                            'text': {'type': 'mrkdwn', 'text': message}
                        }
                    ]
                }

                response = await client.post(self.slack_webhook_url, json=payload)
                return response.status_code == 200

        except Exception as e:
            logger.error(f"Slack notification error: {e}")
            return False

    async def _send_teams(
        self,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]]
    ) -> bool:
        """Send Microsoft Teams notification"""
        try:
            if not self.teams_webhook_url:
                logger.warning("Teams webhook not configured")
                return False

            async with httpx.AsyncClient() as client:
                payload = {
                    '@type': 'MessageCard',
                    '@context': 'https://schema.org/extensions',
                    'summary': title,
                    'themeColor': '0078D4',
                    'title': title,
                    'text': message
                }

                response = await client.post(self.teams_webhook_url, json=payload)
                return response.status_code == 200

        except Exception as e:
            logger.error(f"Teams notification error: {e}")
            return False

    async def send_digest(
        self,
        user_id: int,
        digest_type: str = "daily"
    ) -> bool:
        """
        Send digest notification

        Args:
            user_id: User ID
            digest_type: Digest type (daily, weekly)

        Returns:
            Success status
        """
        try:
            # Gather digest data
            digest_data = await self._gather_digest_data(user_id, digest_type)

            # Send via email
            user_email = f"user{user_id}@example.com"  # Placeholder

            return await email_service.send_template_email(
                to=[user_email],
                template_name='daily_digest',
                template_data=digest_data,
                subject=f"Your {digest_type.title()} Digest"
            )

        except Exception as e:
            logger.error(f"Digest notification error: {e}")
            return False

    async def _gather_digest_data(
        self,
        user_id: int,
        digest_type: str
    ) -> Dict[str, Any]:
        """Gather data for digest"""
        # Placeholder - would query database for actual data
        return {
            'user_name': 'User',
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
            'tasks': [],
            'tasks_count': 0,
            'approvals': [],
            'approvals_count': 0,
            'dashboard_url': 'http://localhost:8501'
        }

    def configure_twilio(
        self,
        account_sid: str,
        auth_token: str,
        phone_number: str
    ):
        """Configure Twilio for SMS"""
        self.twilio_account_sid = account_sid
        self.twilio_auth_token = auth_token
        self.twilio_phone = phone_number
        logger.info("Twilio configured")

    def configure_slack(self, webhook_url: str):
        """Configure Slack webhook"""
        self.slack_webhook_url = webhook_url
        logger.info("Slack configured")

    def configure_teams(self, webhook_url: str):
        """Configure Teams webhook"""
        self.teams_webhook_url = webhook_url
        logger.info("Teams configured")


# Global notification hub instance
notification_hub = NotificationHub()
