"""
Calendar integration tasks
"""
from backend.services.celery_app import celery_app
from backend.core.database import SessionLocal
from typing import Dict, Any


@celery_app.task(name="backend.services.tasks.calendar_tasks.sync_calendar_event")
def sync_calendar_event(event_type: str, event_id: int, action: str):
    """
    Sync event with external calendar (Google Calendar, Outlook, etc.)

    event_type: meeting, task, training, etc.
    event_id: ID of the entity
    action: create, update, delete
    """
    # This would integrate with calendar APIs
    # For now, generate iCalendar format

    db = SessionLocal()
    try:
        if event_type == "meeting":
            from backend.models.workflow import Meeting
            meeting = db.query(Meeting).get(event_id)

            if meeting:
                ical_data = generate_ical_for_meeting(meeting)

                return {
                    "synced": True,
                    "event_type": event_type,
                    "event_id": event_id,
                    "ical": ical_data
                }

        return {
            "synced": False,
            "reason": "Event not found or type not supported"
        }

    finally:
        db.close()


def generate_ical_for_meeting(meeting) -> str:
    """
    Generate iCalendar format for a meeting
    """
    from icalendar import Calendar, Event as ICalEvent
    from datetime import datetime

    cal = Calendar()
    cal.add('prodid', '-//LIMS QMS Platform//Meeting//EN')
    cal.add('version', '2.0')

    event = ICalEvent()
    event.add('summary', meeting.title)
    event.add('description', meeting.description or '')
    event.add('location', meeting.location or meeting.meeting_link or '')

    # Combine date and time
    if meeting.meeting_date and meeting.start_time:
        try:
            # Parse time (assuming format HH:MM)
            hour, minute = meeting.start_time.split(':')
            start_dt = datetime.combine(
                meeting.meeting_date,
                datetime.min.time().replace(hour=int(hour), minute=int(minute))
            )
            event.add('dtstart', start_dt)

            if meeting.end_time:
                hour, minute = meeting.end_time.split(':')
                end_dt = datetime.combine(
                    meeting.meeting_date,
                    datetime.min.time().replace(hour=int(hour), minute=int(minute))
                )
                event.add('dtend', end_dt)

        except:
            # If parsing fails, just use date
            event.add('dtstart', meeting.meeting_date)
    else:
        event.add('dtstart', meeting.meeting_date)

    event.add('uid', f'meeting-{meeting.id}@limsqms.platform')

    # Add attendees
    if meeting.attendees and isinstance(meeting.attendees, list):
        for attendee_id in meeting.attendees:
            # Would fetch user email here
            pass

    cal.add_component(event)

    return cal.to_ical().decode('utf-8')


@celery_app.task(name="backend.services.tasks.calendar_tasks.generate_project_timeline")
def generate_project_timeline(project_id: int):
    """
    Generate Gantt chart data for a project
    """
    from backend.models.workflow import Project, Task, Milestone

    db = SessionLocal()
    try:
        project = db.query(Project).get(project_id)

        if not project:
            return {"error": "Project not found"}

        # Get all tasks and milestones
        tasks = db.query(Task).filter(
            Task.project_id == project_id,
            Task.is_deleted == False
        ).all()

        milestones = db.query(Milestone).filter(
            Milestone.project_id == project_id,
            Milestone.is_deleted == False
        ).all()

        # Build Gantt data
        gantt_data = {
            "project": {
                "id": project.id,
                "name": project.name,
                "start": project.start_date.isoformat() if project.start_date else None,
                "end": project.end_date.isoformat() if project.end_date else None,
                "progress": project.progress
            },
            "tasks": [
                {
                    "id": task.id,
                    "name": task.title,
                    "start": task.start_date.isoformat() if task.start_date else None,
                    "end": task.due_date.isoformat() if task.due_date else None,
                    "progress": task.progress,
                    "dependencies": task.depends_on or [],
                    "assignee": task.assigned_to_id,
                    "milestone_id": task.milestone_id
                }
                for task in tasks
            ],
            "milestones": [
                {
                    "id": milestone.id,
                    "name": milestone.name,
                    "date": milestone.due_date.isoformat(),
                    "status": milestone.status.value
                }
                for milestone in milestones
            ]
        }

        return gantt_data

    finally:
        db.close()
