"""
Integration API Endpoints
API endpoints for integration hub, AI orchestration, webhooks, etc.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from backend.integrations.ai_orchestrator import ai_orchestrator
from backend.integrations.events import event_bus, Event, EventType
from backend.integrations.notifications import notification_hub, NotificationChannel, NotificationPriority
from backend.integrations.tasks.notifications import send_notification_task
from backend.integrations.tasks.etl import export_data, import_data
from backend.integrations.tasks.backups import backup_database, backup_files
from backend.api.dependencies.auth import get_current_user

router = APIRouter()


# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    actions: List[Dict[str, Any]]
    error: bool


class SearchRequest(BaseModel):
    query: str
    scope: Optional[List[str]] = None


class DataExtractionRequest(BaseModel):
    document_content: str
    document_type: str
    fields_to_extract: List[str]


class ComplianceCheckRequest(BaseModel):
    document_type: str
    content: Dict[str, Any]
    standards: List[str]


class NotificationRequest(BaseModel):
    user_id: int
    title: str
    message: str
    channels: List[str]
    priority: str = "normal"
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None


class ExportRequest(BaseModel):
    export_type: str
    format: str = "excel"
    filters: Optional[Dict[str, Any]] = None


class ImportRequest(BaseModel):
    file_path: str
    import_type: str
    mapping: Optional[Dict[str, str]] = None


class WebhookPayload(BaseModel):
    event_type: str
    source: str
    data: Dict[str, Any]
    timestamp: Optional[datetime] = None


# AI Orchestration Endpoints
@router.post("/ai/chat", response_model=ChatResponse)
async def ai_chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Chat with Claude AI assistant

    Args:
        request: Chat request with message and context
        current_user: Current authenticated user

    Returns:
        AI response with suggestions and actions
    """
    try:
        result = await ai_orchestrator.chat(
            message=request.message,
            user_id=current_user['id'],
            context=request.context,
            conversation_id=request.conversation_id
        )

        return ChatResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/search")
async def smart_search(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """Natural language search"""
    try:
        result = await ai_orchestrator.smart_search(
            query=request.query,
            user_id=current_user['id'],
            scope=request.scope
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/extract-data")
async def extract_document_data(
    request: DataExtractionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Extract structured data from documents using AI"""
    try:
        result = await ai_orchestrator.extract_data_from_document(
            document_content=request.document_content,
            document_type=request.document_type,
            fields_to_extract=request.fields_to_extract
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/check-compliance")
async def check_compliance(
    request: ComplianceCheckRequest,
    current_user: dict = Depends(get_current_user)
):
    """Check document compliance with standards"""
    try:
        result = await ai_orchestrator.check_compliance(
            document_type=request.document_type,
            content=request.content,
            standards=request.standards
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/generate-report")
async def generate_report(
    prompt: str,
    data_sources: List[str],
    format: str = "markdown",
    current_user: dict = Depends(get_current_user)
):
    """Generate report from natural language prompt"""
    try:
        result = await ai_orchestrator.generate_report_from_prompt(
            prompt=prompt,
            data_sources=data_sources,
            format=format
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Notification Endpoints
@router.post("/notifications/send")
async def send_notification(
    request: NotificationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Send notification through multiple channels"""
    try:
        # Queue notification as background task
        background_tasks.add_task(
            send_notification_task,
            user_id=request.user_id,
            title=request.title,
            message=request.message,
            channels=request.channels,
            priority=request.priority
        )

        return {
            "status": "queued",
            "message": "Notification queued for delivery"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/user/{user_id}")
async def get_user_notifications(
    user_id: int,
    unread_only: bool = True,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get user notifications"""
    # Placeholder - would query database
    return {
        "notifications": [],
        "unread_count": 0,
        "total": 0
    }


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Mark notification as read"""
    # Placeholder - would update database
    return {"status": "success"}


# Event Management Endpoints
@router.post("/events/publish")
async def publish_event(
    event_type: str,
    data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Publish event to event bus"""
    try:
        event = Event(
            type=EventType(event_type),
            source="api",
            data=data,
            user_id=current_user['id']
        )

        await event_bus.publish(event)

        return {
            "status": "published",
            "event_type": event_type
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/history/{event_type}")
async def get_event_history(
    event_type: str,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get event history"""
    try:
        events = await event_bus.get_event_history(
            event_type=EventType(event_type),
            limit=limit
        )

        return {
            "events": [e.to_dict() for e in events],
            "count": len(events)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Data Exchange Endpoints
@router.post("/export")
async def export_data_endpoint(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Export data to various formats"""
    try:
        # Queue export as background task
        task = export_data.delay(
            export_type=request.export_type,
            format=request.format,
            filters=request.filters
        )

        return {
            "status": "queued",
            "task_id": task.id,
            "message": "Export queued for processing"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_data_endpoint(
    request: ImportRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Import data from external files"""
    try:
        # Queue import as background task
        task = import_data.delay(
            file_path=request.file_path,
            import_type=request.import_type,
            mapping=request.mapping
        )

        return {
            "status": "queued",
            "task_id": task.id,
            "message": "Import queued for processing"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Webhook Endpoints
@router.post("/webhooks/{webhook_name}")
async def receive_webhook(
    webhook_name: str,
    payload: WebhookPayload
):
    """
    Receive webhook from external systems
    No authentication required (use webhook secrets in production)
    """
    try:
        # Process webhook based on name
        event = Event(
            type=EventType(payload.event_type),
            source=f"webhook:{webhook_name}",
            data=payload.data,
            timestamp=payload.timestamp or datetime.utcnow()
        )

        await event_bus.publish(event)

        return {
            "status": "received",
            "webhook": webhook_name,
            "event_type": payload.event_type
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# System Management Endpoints
@router.post("/system/backup/database")
async def trigger_database_backup(
    current_user: dict = Depends(get_current_user)
):
    """Trigger manual database backup"""
    try:
        task = backup_database.delay()
        return {
            "status": "queued",
            "task_id": task.id,
            "message": "Database backup queued"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system/backup/files")
async def trigger_file_backup(
    current_user: dict = Depends(get_current_user)
):
    """Trigger manual file backup"""
    try:
        task = backup_files.delay()
        return {
            "status": "queued",
            "task_id": task.id,
            "message": "File backup queued"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/health")
async def system_health():
    """Get system health status"""
    from backend.integrations.tasks.monitoring import system_health_check

    try:
        health = system_health_check()
        return health

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/metrics")
async def system_metrics(
    current_user: dict = Depends(get_current_user)
):
    """Get system performance metrics"""
    from backend.integrations.tasks.monitoring import collect_performance_metrics

    try:
        metrics = collect_performance_metrics()
        return metrics

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Task Status Endpoint
@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get status of background task"""
    from backend.integrations.celery_app import celery_app

    try:
        task = celery_app.AsyncResult(task_id)

        return {
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.ready() else None,
            "error": str(task.info) if task.failed() else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
