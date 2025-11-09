"""
Event-Driven Architecture - Event Bus and Pub/Sub System
Enables inter-module communication and workflow orchestration
"""
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
from enum import Enum
import asyncio
import json
from dataclasses import dataclass, asdict
from redis import asyncio as aioredis
from backend.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """System-wide event types"""
    # Document events
    DOCUMENT_CREATED = "document.created"
    DOCUMENT_UPDATED = "document.updated"
    DOCUMENT_APPROVED = "document.approved"
    DOCUMENT_REJECTED = "document.rejected"
    DOCUMENT_ARCHIVED = "document.archived"

    # Form events
    FORM_SUBMITTED = "form.submitted"
    FORM_APPROVED = "form.approved"
    FORM_REJECTED = "form.rejected"

    # Project events
    PROJECT_CREATED = "project.created"
    PROJECT_STARTED = "project.started"
    PROJECT_COMPLETED = "project.completed"
    PROJECT_CANCELLED = "project.cancelled"

    # Task events
    TASK_CREATED = "task.created"
    TASK_ASSIGNED = "task.assigned"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_OVERDUE = "task.overdue"

    # Workflow events
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_STEP_COMPLETED = "workflow.step_completed"
    WORKFLOW_APPROVED = "workflow.approved"
    WORKFLOW_REJECTED = "workflow.rejected"
    WORKFLOW_COMPLETED = "workflow.completed"

    # Quality events
    NC_CREATED = "quality.nc_created"
    CAPA_CREATED = "quality.capa_created"
    AUDIT_SCHEDULED = "quality.audit_scheduled"
    AUDIT_COMPLETED = "quality.audit_completed"

    # HR events
    EMPLOYEE_ONBOARDED = "hr.employee_onboarded"
    TRAINING_COMPLETED = "hr.training_completed"
    TRAINING_DUE = "hr.training_due"
    LEAVE_REQUESTED = "hr.leave_requested"
    LEAVE_APPROVED = "hr.leave_approved"

    # Procurement events
    RFQ_CREATED = "procurement.rfq_created"
    VENDOR_RESPONDED = "procurement.vendor_responded"
    PO_CREATED = "procurement.po_created"
    PO_APPROVED = "procurement.po_approved"
    GOODS_RECEIVED = "procurement.goods_received"

    # Financial events
    INVOICE_CREATED = "financial.invoice_created"
    INVOICE_PAID = "financial.invoice_paid"
    PAYMENT_PENDING = "financial.payment_pending"
    PAYMENT_COMPLETED = "financial.payment_completed"

    # CRM events
    LEAD_CREATED = "crm.lead_created"
    LEAD_CONVERTED = "crm.lead_converted"
    OPPORTUNITY_WON = "crm.opportunity_won"
    OPPORTUNITY_LOST = "crm.opportunity_lost"

    # System events
    USER_LOGGED_IN = "system.user_logged_in"
    USER_LOGGED_OUT = "system.user_logged_out"
    BACKUP_COMPLETED = "system.backup_completed"
    SYSTEM_ERROR = "system.error"
    NOTIFICATION_SENT = "system.notification_sent"


@dataclass
class Event:
    """Event data structure"""
    type: EventType
    source: str
    data: Dict[str, Any]
    timestamp: datetime = None
    user_id: Optional[int] = None
    organization_id: Optional[int] = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        data = asdict(self)
        data['type'] = self.type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary"""
        data['type'] = EventType(data['type'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class EventBus:
    """
    Central Event Bus for pub/sub messaging
    Uses Redis for distributed event handling
    """

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.running = False

    async def connect(self):
        """Connect to Redis"""
        if not self.redis:
            self.redis = await aioredis.from_url(settings.REDIS_URL)
            logger.info("EventBus connected to Redis")

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            self.redis = None
            logger.info("EventBus disconnected from Redis")

    async def publish(self, event: Event):
        """
        Publish event to all subscribers

        Args:
            event: Event to publish
        """
        await self.connect()

        # Store event in Redis stream for persistence
        event_data = json.dumps(event.to_dict(), default=str)
        await self.redis.xadd(
            f"events:{event.type.value}",
            {"data": event_data},
            maxlen=1000  # Keep last 1000 events
        )

        # Publish to pub/sub channel
        await self.redis.publish(
            f"events:{event.type.value}",
            event_data
        )

        # Call local subscribers
        if event.type in self.subscribers:
            for callback in self.subscribers[event.type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"Error in event subscriber: {e}")

        logger.debug(f"Published event: {event.type.value}")

    def subscribe(self, event_type: EventType, callback: Callable):
        """
        Subscribe to event type

        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.info(f"Subscribed to event: {event_type.value}")

    def unsubscribe(self, event_type: EventType, callback: Callable):
        """
        Unsubscribe from event type

        Args:
            event_type: Type of event to unsubscribe from
            callback: Function to remove
        """
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
            logger.info(f"Unsubscribed from event: {event_type.value}")

    async def listen(self, event_types: List[EventType] = None):
        """
        Listen for events from Redis pub/sub

        Args:
            event_types: List of event types to listen for (None = all)
        """
        await self.connect()

        pubsub = self.redis.pubsub()

        # Subscribe to channels
        if event_types:
            channels = [f"events:{et.value}" for et in event_types]
        else:
            channels = [f"events:*"]

        await pubsub.psubscribe(*channels)

        self.running = True
        logger.info(f"EventBus listening to channels: {channels}")

        try:
            while self.running:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message and message['type'] == 'pmessage':
                    event_data = json.loads(message['data'])
                    event = Event.from_dict(event_data)

                    # Call subscribers
                    if event.type in self.subscribers:
                        for callback in self.subscribers[event.type]:
                            try:
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(event)
                                else:
                                    callback(event)
                            except Exception as e:
                                logger.error(f"Error in event listener: {e}")

                await asyncio.sleep(0.01)  # Small delay to prevent CPU spinning

        finally:
            await pubsub.unsubscribe()
            await pubsub.close()

    async def get_event_history(
        self,
        event_type: EventType,
        limit: int = 100
    ) -> List[Event]:
        """
        Get event history from Redis stream

        Args:
            event_type: Type of event to retrieve
            limit: Maximum number of events to retrieve

        Returns:
            List of events
        """
        await self.connect()

        events = []
        stream_data = await self.redis.xrevrange(
            f"events:{event_type.value}",
            count=limit
        )

        for _, data in stream_data:
            event_data = json.loads(data[b'data'])
            events.append(Event.from_dict(event_data))

        return events


# Global event bus instance
event_bus = EventBus()


# Event decorators for easy subscription
def on_event(event_type: EventType):
    """Decorator to subscribe function to event"""
    def decorator(func: Callable):
        event_bus.subscribe(event_type, func)
        return func
    return decorator


# Example event handlers
@on_event(EventType.DOCUMENT_APPROVED)
async def on_document_approved(event: Event):
    """Handle document approval - trigger notifications"""
    logger.info(f"Document approved: {event.data.get('document_id')}")
    # Trigger notification
    # Update related workflows
    # Create audit trail


@on_event(EventType.TASK_OVERDUE)
async def on_task_overdue(event: Event):
    """Handle overdue tasks - send reminders"""
    logger.warning(f"Task overdue: {event.data.get('task_id')}")
    # Send escalation notification
    # Update task priority


@on_event(EventType.WORKFLOW_COMPLETED)
async def on_workflow_completed(event: Event):
    """Handle workflow completion - trigger next steps"""
    logger.info(f"Workflow completed: {event.data.get('workflow_id')}")
    # Archive workflow
    # Notify stakeholders
    # Update project status
