"""
Calendar Integration
Google Calendar, Outlook, and iCalendar support
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from icalendar import Calendar, Event as iCalEvent
import httpx
import logging

logger = logging.getLogger(__name__)


class CalendarService:
    """Calendar service for scheduling and event management"""

    def __init__(self):
        self.google_api_key: Optional[str] = None
        self.outlook_api_key: Optional[str] = None

    async def create_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        reminder_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Create calendar event

        Args:
            title: Event title
            start_time: Start time
            end_time: End time
            description: Event description
            location: Event location
            attendees: List of attendee emails
            reminder_minutes: Reminder time before event

        Returns:
            Created event details
        """
        try:
            # Create iCalendar event
            cal = Calendar()
            cal.add('prodid', '-//LIMS-QMS Organization OS//Calendar//EN')
            cal.add('version', '2.0')

            event = iCalEvent()
            event.add('summary', title)
            event.add('dtstart', start_time)
            event.add('dtend', end_time)

            if description:
                event.add('description', description)

            if location:
                event.add('location', location)

            if attendees:
                for attendee in attendees:
                    event.add('attendee', f'mailto:{attendee}')

            # Add reminder
            event.add('valarm', {
                'action': 'DISPLAY',
                'trigger': timedelta(minutes=-reminder_minutes),
                'description': 'Reminder'
            })

            cal.add_component(event)

            logger.info(f"Created calendar event: {title}")
            return {
                'success': True,
                'event': {
                    'title': title,
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'ical': cal.to_ical().decode('utf-8')
                }
            }

        except Exception as e:
            logger.error(f"Failed to create calendar event: {e}")
            return {'success': False, 'error': str(e)}

    async def sync_with_google_calendar(
        self,
        calendar_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Sync with Google Calendar

        Args:
            calendar_id: Google Calendar ID
            access_token: OAuth access token

        Returns:
            Sync status
        """
        try:
            async with httpx.AsyncClient() as client:
                # Fetch events from Google Calendar
                response = await client.get(
                    f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events",
                    headers={'Authorization': f'Bearer {access_token}'}
                )

                if response.status_code == 200:
                    events = response.json().get('items', [])
                    logger.info(f"Synced {len(events)} events from Google Calendar")
                    return {'success': True, 'events': events}
                else:
                    return {'success': False, 'error': 'Failed to fetch events'}

        except Exception as e:
            logger.error(f"Google Calendar sync error: {e}")
            return {'success': False, 'error': str(e)}

    async def sync_with_outlook(
        self,
        user_email: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Sync with Outlook Calendar

        Args:
            user_email: User's email
            access_token: OAuth access token

        Returns:
            Sync status
        """
        try:
            async with httpx.AsyncClient() as client:
                # Fetch events from Outlook
                response = await client.get(
                    f"https://graph.microsoft.com/v1.0/users/{user_email}/calendar/events",
                    headers={'Authorization': f'Bearer {access_token}'}
                )

                if response.status_code == 200:
                    events = response.json().get('value', [])
                    logger.info(f"Synced {len(events)} events from Outlook")
                    return {'success': True, 'events': events}
                else:
                    return {'success': False, 'error': 'Failed to fetch events'}

        except Exception as e:
            logger.error(f"Outlook sync error: {e}")
            return {'success': False, 'error': str(e)}

    async def get_availability(
        self,
        user_emails: List[str],
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, List[Dict[str, datetime]]]:
        """
        Get availability for multiple users

        Args:
            user_emails: List of user emails
            start_time: Start of time range
            end_time: End of time range

        Returns:
            Availability for each user
        """
        # Placeholder for availability checking
        # In production, integrate with calendar APIs
        availability = {}
        for email in user_emails:
            availability[email] = [
                {
                    'start': start_time,
                    'end': end_time,
                    'available': True
                }
            ]

        return availability

    async def find_meeting_slot(
        self,
        attendees: List[str],
        duration_minutes: int,
        preferred_start: datetime,
        preferred_end: datetime
    ) -> Optional[Dict[str, datetime]]:
        """
        Find available meeting slot for all attendees

        Args:
            attendees: List of attendee emails
            duration_minutes: Meeting duration
            preferred_start: Preferred start time
            preferred_end: Preferred end time

        Returns:
            Suggested meeting slot
        """
        try:
            # Get availability for all attendees
            availability = await self.get_availability(
                attendees,
                preferred_start,
                preferred_end
            )

            # Find common available slots
            # Simplified logic - in production, implement proper slot finding
            suggested_slot = {
                'start': preferred_start,
                'end': preferred_start + timedelta(minutes=duration_minutes)
            }

            logger.info(f"Found meeting slot for {len(attendees)} attendees")
            return suggested_slot

        except Exception as e:
            logger.error(f"Failed to find meeting slot: {e}")
            return None


# Global calendar service instance
calendar_service = CalendarService()
