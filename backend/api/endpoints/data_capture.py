"""
Data Capture & Filling Engine API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.core.database import get_db
from backend.api.dependencies.auth import get_current_user
from backend.models import User, FormRecord, RecordStatusEnum
from backend.services import (
    ValidationService,
    WorkflowService,
    NotificationService,
    RecordService,
    BulkUploadService,
    SignatureService
)
from backend.schemas.data_capture import (
    RecordCreate, RecordUpdate, RecordResponse, RecordListResponse,
    WorkflowAction, CommentCreate, CommentResponse, WorkflowHistoryResponse,
    ValidationRequest, ValidationResponse,
    DraftSave, DraftResponse,
    SignatureCreate, SignatureResponse,
    BulkUploadResponse,
    NotificationResponse,
    TraceabilityLinkResponse
)
import os
from backend.core.config import settings

router = APIRouter()


# ============================================================================
# RECORD MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/records", response_model=RecordResponse)
async def create_record(
    record_data: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new form record"""
    try:
        record_service = RecordService(db)
        record = record_service.create_record(
            template_id=record_data.template_id,
            user_id=current_user.id,
            values=record_data.values,
            title=record_data.title,
            metadata=record_data.metadata,
            auto_submit=record_data.auto_submit
        )

        # Auto-submit if requested
        if record_data.auto_submit:
            workflow_service = WorkflowService(db)
            success, message = workflow_service.submit_record(record.id, current_user.id)
            if success:
                notification_service = NotificationService(db)
                notification_service.notify_submission(record.id)

        return record_service.get_record(record.id, include_values=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/records/{record_id}", response_model=RecordResponse)
async def get_record(
    record_id: int,
    include_values: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get record details"""
    try:
        record_service = RecordService(db)
        record = record_service.get_record(record_id, include_values=include_values)
        return record
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/records/{record_id}", response_model=RecordResponse)
async def update_record(
    record_id: int,
    record_data: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update existing record"""
    try:
        record_service = RecordService(db)
        record = record_service.update_record(
            record_id=record_id,
            user_id=current_user.id,
            values=record_data.values,
            title=record_data.title,
            metadata=record_data.metadata
        )
        return record_service.get_record(record.id, include_values=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/records", response_model=RecordListResponse)
async def list_records(
    template_id: Optional[int] = None,
    status: Optional[str] = None,
    doer_id: Optional[int] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List form records with filters"""
    query = db.query(FormRecord)

    if template_id:
        query = query.filter(FormRecord.template_id == template_id)
    if status:
        query = query.filter(FormRecord.status == RecordStatusEnum(status))
    if doer_id:
        query = query.filter(FormRecord.doer_id == doer_id)

    total = query.count()
    records = query.order_by(FormRecord.created_at.desc()).offset(skip).limit(limit).all()

    record_service = RecordService(db)
    record_list = [record_service.get_record(r.id, include_values=False) for r in records]

    return {
        "total": total,
        "records": record_list,
        "skip": skip,
        "limit": limit
    }


# ============================================================================
# WORKFLOW ENDPOINTS
# ============================================================================

@router.post("/records/{record_id}/submit")
async def submit_record(
    record_id: int,
    comments: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit record for review"""
    workflow_service = WorkflowService(db)

    # Check permissions
    can_submit, msg = workflow_service.check_workflow_permissions(record_id, current_user.id, "submit")
    if not can_submit:
        raise HTTPException(status_code=403, detail=msg)

    success, message = workflow_service.submit_record(record_id, current_user.id, comments)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Send notification
    notification_service = NotificationService(db)
    notification_service.notify_submission(record_id)

    return {"success": True, "message": message}


@router.post("/records/{record_id}/review")
async def review_record(
    record_id: int,
    action_data: WorkflowAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Checker reviews the record"""
    workflow_service = WorkflowService(db)

    # Check permissions
    can_review, msg = workflow_service.check_workflow_permissions(record_id, current_user.id, "review")
    if not can_review:
        raise HTTPException(status_code=403, detail=msg)

    success, message = workflow_service.review_record(
        record_id,
        current_user.id,
        action_data.action,
        action_data.comments,
        action_data.metadata
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Send notification
    notification_service = NotificationService(db)
    approved = action_data.action == "approve"
    notification_service.notify_review_complete(record_id, approved)

    return {"success": True, "message": message}


@router.post("/records/{record_id}/approve")
async def approve_record(
    record_id: int,
    action_data: WorkflowAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approver approves the record"""
    workflow_service = WorkflowService(db)

    # Check permissions
    can_approve, msg = workflow_service.check_workflow_permissions(record_id, current_user.id, "approve")
    if not can_approve:
        raise HTTPException(status_code=403, detail=msg)

    success, message = workflow_service.approve_record(
        record_id,
        current_user.id,
        action_data.action,
        action_data.comments,
        action_data.metadata
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Send notification
    notification_service = NotificationService(db)
    approved = action_data.action == "approve"
    notification_service.notify_approval(record_id, approved)

    return {"success": True, "message": message}


@router.post("/records/{record_id}/revise")
async def revise_record(
    record_id: int,
    record_data: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Doer revises the record after revision request"""
    workflow_service = WorkflowService(db)

    # Check permissions
    can_revise, msg = workflow_service.check_workflow_permissions(record_id, current_user.id, "revise")
    if not can_revise:
        raise HTTPException(status_code=403, detail=msg)

    success, message = workflow_service.revise_record(
        record_id,
        current_user.id,
        record_data.values
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Update the record with new values
    record_service = RecordService(db)
    record_service.update_record(
        record_id,
        current_user.id,
        record_data.values,
        record_data.title,
        record_data.metadata
    )

    return {"success": True, "message": message}


@router.get("/records/{record_id}/history", response_model=List[WorkflowHistoryResponse])
async def get_workflow_history(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workflow history for a record"""
    workflow_service = WorkflowService(db)
    return workflow_service.get_workflow_history(record_id)


@router.get("/pending-approvals", response_model=List[dict])
async def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get records pending approval for current user"""
    workflow_service = WorkflowService(db)
    return workflow_service.get_pending_approvals(current_user.id)


# ============================================================================
# COMMENT ENDPOINTS
# ============================================================================

@router.post("/records/{record_id}/comments", response_model=CommentResponse)
async def add_comment(
    record_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add comment to record"""
    workflow_service = WorkflowService(db)
    comment = workflow_service.add_comment(
        record_id,
        current_user.id,
        comment_data.content,
        comment_data.field_id,
        comment_data.comment_type,
        comment_data.parent_comment_id
    )

    # Send notification
    notification_service = NotificationService(db)
    notification_service.notify_comment(record_id, current_user.id, comment_data.content)

    return workflow_service.get_comments(record_id)[0]


@router.get("/records/{record_id}/comments", response_model=List[CommentResponse])
async def get_comments(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all comments for a record"""
    workflow_service = WorkflowService(db)
    return workflow_service.get_comments(record_id)


@router.put("/comments/{comment_id}/resolve")
async def resolve_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark comment as resolved"""
    workflow_service = WorkflowService(db)
    success, message = workflow_service.resolve_comment(comment_id, current_user.id)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message}


# ============================================================================
# VALIDATION ENDPOINTS
# ============================================================================

@router.post("/validate", response_model=ValidationResponse)
async def validate_data(
    validation_data: ValidationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate form data"""
    validation_service = ValidationService(db)

    is_valid, errors, warnings = validation_service.validate_record(
        validation_data.template_id,
        validation_data.values
    )

    completion_percentage = validation_service.calculate_completion_percentage(
        validation_data.template_id,
        validation_data.values
    )

    validation_score = validation_service.calculate_validation_score(errors, warnings)

    duplicates = validation_service.check_duplicates(
        validation_data.template_id,
        validation_data.values
    )

    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "completion_percentage": completion_percentage,
        "validation_score": validation_score,
        "duplicates": duplicates
    }


# ============================================================================
# DRAFT ENDPOINTS
# ============================================================================

@router.post("/drafts", response_model=DraftResponse)
async def save_draft(
    draft_data: DraftSave,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Auto-save draft"""
    record_service = RecordService(db)
    draft = record_service.save_draft(
        draft_data.template_id,
        current_user.id,
        draft_data.values,
        draft_data.record_id
    )

    return {
        "id": draft.id,
        "draft_data": draft.draft_data,
        "last_saved_at": draft.last_saved_at
    }


@router.get("/drafts/{template_id}")
async def get_draft(
    template_id: int,
    record_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get saved draft"""
    record_service = RecordService(db)
    draft = record_service.get_draft(template_id, current_user.id, record_id)

    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    return draft


@router.delete("/drafts/{draft_id}")
async def delete_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete draft"""
    record_service = RecordService(db)
    success = record_service.delete_draft(draft_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Draft not found")

    return {"success": True, "message": "Draft deleted"}


# ============================================================================
# SIGNATURE ENDPOINTS
# ============================================================================

@router.post("/records/{record_id}/signatures", response_model=SignatureResponse)
async def capture_signature(
    record_id: int,
    signature_data: SignatureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Capture digital signature"""
    try:
        signature_service = SignatureService(db)
        signature = signature_service.capture_signature(
            record_id,
            current_user.id,
            signature_data.signature_type,
            signature_data.signature_data,
            signature_data.signature_method,
            signature_data.ip_address,
            signature_data.device_info,
            signature_data.certificate_info
        )

        return signature_service.get_record_signatures(record_id)[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/records/{record_id}/signatures", response_model=List[SignatureResponse])
async def get_signatures(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all signatures for a record"""
    signature_service = SignatureService(db)
    return signature_service.get_record_signatures(record_id)


@router.get("/signatures/{signature_id}/verify")
async def verify_signature(
    signature_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify signature"""
    signature_service = SignatureService(db)
    try:
        verification = signature_service.verify_signature(signature_id)
        return verification
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/records/{record_id}/signature-report")
async def get_signature_report(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get signature verification report"""
    signature_service = SignatureService(db)
    try:
        report = signature_service.create_signature_report(record_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# BULK UPLOAD ENDPOINTS
# ============================================================================

@router.post("/bulk-upload/{template_id}", response_model=dict)
async def bulk_upload(
    template_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload bulk data from Excel/CSV"""
    # Validate file type
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in ['csv', 'xlsx', 'xls']:
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV and Excel files are supported.")

    # Save file
    upload_dir = os.path.join(settings.UPLOAD_DIR, "bulk_uploads")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, f"{current_user.id}_{int(datetime.now().timestamp())}_{file.filename}")

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Process upload
    try:
        bulk_service = BulkUploadService(db)
        upload_id, result = bulk_service.process_upload(
            template_id,
            current_user.id,
            file_path,
            file.filename,
            file_ext
        )

        # Send notification
        notification_service = NotificationService(db)
        notification_service.notify_bulk_upload_complete(
            current_user.id,
            upload_id,
            result["failed_rows"] == 0,
            result["total_rows"],
            result["successful_rows"],
            result["failed_rows"]
        )

        return {
            "upload_id": upload_id,
            "success": True,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/bulk-uploads/{upload_id}", response_model=BulkUploadResponse)
async def get_bulk_upload_status(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get bulk upload status"""
    try:
        bulk_service = BulkUploadService(db)
        return bulk_service.get_upload_status(upload_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/templates/{template_id}/bulk-template")
async def download_bulk_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download CSV template for bulk upload"""
    from fastapi.responses import Response

    bulk_service = BulkUploadService(db)
    csv_content = bulk_service.generate_template_csv(template_id)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=template_{template_id}.csv"}
    )


# ============================================================================
# TRACEABILITY ENDPOINTS
# ============================================================================

@router.post("/records/{record_id}/link")
async def create_traceability_link(
    record_id: int,
    parent_type: str,
    parent_id: int,
    link_type: str = "related",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create traceability link"""
    record_service = RecordService(db)
    link = record_service.link_to_parent(record_id, parent_type, parent_id, link_type)

    return {
        "id": link.id,
        "source_type": link.source_entity_type,
        "source_id": link.source_entity_id,
        "target_type": link.target_entity_type,
        "target_id": link.target_entity_id,
        "link_type": link.link_type
    }


@router.get("/records/{record_id}/links", response_model=List[TraceabilityLinkResponse])
async def get_traceability_links(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get traceability links for a record"""
    record_service = RecordService(db)
    return record_service.get_record_links(record_id)


# ============================================================================
# NOTIFICATION ENDPOINTS
# ============================================================================

@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user notifications"""
    notification_service = NotificationService(db)
    return notification_service.get_user_notifications(current_user.id, unread_only, limit)


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark notification as read"""
    notification_service = NotificationService(db)
    success = notification_service.mark_as_read(notification_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")

    return {"success": True}


@router.put("/notifications/mark-all-read")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read"""
    notification_service = NotificationService(db)
    count = notification_service.mark_all_as_read(current_user.id)

    return {"success": True, "count": count}


@router.get("/notifications/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get unread notification count"""
    notification_service = NotificationService(db)
    count = notification_service.get_unread_count(current_user.id)

    return {"count": count}
