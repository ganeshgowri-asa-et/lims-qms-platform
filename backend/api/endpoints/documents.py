"""
Document Management API endpoints - Comprehensive implementation
Provides RESTful API for document management with full workflow support
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.document import (
    DocumentLevelEnum,
    DocumentTypeEnum,
    DocumentStatusEnum,
    StandardEnum,
    ApprovalActionEnum
)
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from backend.services import DocumentService
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import io

router = APIRouter()


# ============= Pydantic Schemas =============

class DocumentCreate(BaseModel):
    title: str
    level: DocumentLevelEnum
    document_type: Optional[DocumentTypeEnum] = None
    category: Optional[str] = None
    standard: Optional[StandardEnum] = None
    department: Optional[str] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    scope: Optional[str] = None
    parent_document_id: Optional[int] = None
    is_template: bool = False
    template_document_id: Optional[int] = None
    document_owner_id: Optional[int] = None
    manual_number: Optional[str] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    metadata: Optional[dict] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    scope: Optional[str] = None
    category: Optional[str] = None
    standard: Optional[StandardEnum] = None
    department: Optional[str] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    metadata: Optional[dict] = None


class DocumentMetadataUpdate(BaseModel):
    table_of_contents: Optional[List[dict]] = None
    responsibilities: Optional[List[dict]] = None
    equipment_required: Optional[List[dict]] = None
    software_required: Optional[List[dict]] = None
    resources_required: Optional[List[dict]] = None
    process_flowchart: Optional[str] = None
    value_stream_map: Optional[str] = None
    turtle_diagram: Optional[str] = None
    infographics: Optional[List[dict]] = None
    kpi_definitions: Optional[List[dict]] = None
    measurement_frequency: Optional[str] = None
    annexures: Optional[List[dict]] = None
    references: Optional[List[dict]] = None
    risk_assessment: Optional[List[dict]] = None
    process_analysis: Optional[str] = None
    nc_control_procedure: Optional[str] = None
    nc_escalation_matrix: Optional[List[dict]] = None
    training_required: Optional[List[dict]] = None
    safety_requirements: Optional[List[dict]] = None
    compliance_checklist: Optional[List[dict]] = None
    custom_fields: Optional[dict] = None


class WorkflowSubmit(BaseModel):
    checker_id: int
    comments: Optional[str] = None


class WorkflowReview(BaseModel):
    action: str  # 'approve', 'reject', 'request_revision'
    approver_id: Optional[int] = None
    comments: Optional[str] = None
    signature: Optional[str] = None


class WorkflowApprove(BaseModel):
    action: str  # 'approve', 'reject'
    comments: Optional[str] = None
    signature: Optional[str] = None


class DocumentLinkCreate(BaseModel):
    target_document_id: int
    link_type: str
    description: Optional[str] = None
    is_bidirectional: bool = False
    strength: str = "normal"


class AccessGrant(BaseModel):
    user_id: Optional[int] = None
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    can_view: bool = True
    can_edit: bool = False
    can_review: bool = False
    can_approve: bool = False
    can_delete: bool = False
    valid_until: Optional[datetime] = None


class RetentionPolicyCreate(BaseModel):
    policy_name: str
    retention_years: int
    retention_months: int = 0
    document_level: Optional[DocumentLevelEnum] = None
    document_type: Optional[DocumentTypeEnum] = None
    category: Optional[str] = None
    auto_archive: bool = False
    auto_destroy: bool = False
    require_approval_for_destruction: bool = True
    legal_requirement: bool = False
    regulation_reference: Optional[str] = None
    description: Optional[str] = None


class TemplateIndexCreate(BaseModel):
    document_id: int
    template_name: str
    template_code: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    is_dynamic: bool = False
    fields_schema: Optional[dict] = None
    validation_rules: Optional[dict] = None
    search_keywords: Optional[List[str]] = None
    description: Optional[str] = None


# ============= Document CRUD Endpoints =============

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new document"""
    try:
        service = DocumentService(db)
        result = service.create_document(
            title=document.title,
            level=document.level,
            created_by_id=current_user.id,
            document_type=document.document_type,
            category=document.category,
            standard=document.standard,
            department=document.department,
            description=document.description,
            purpose=document.purpose,
            scope=document.scope,
            parent_document_id=document.parent_document_id,
            is_template=document.is_template,
            template_document_id=document.template_document_id,
            document_owner_id=document.document_owner_id,
            manual_number=document.manual_number,
            tags=document.tags,
            keywords=document.keywords,
            metadata=document.metadata
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{document_id}")
async def get_document(
    document_id: int,
    include_metadata: bool = Query(False, description="Include extended metadata"),
    include_versions: bool = Query(False, description="Include version history"),
    include_links: bool = Query(False, description="Include document links"),
    include_approvals: bool = Query(False, description="Include approval history"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document by ID with optional related data"""
    try:
        service = DocumentService(db)
        result = service.get_document(
            document_id=document_id,
            user_id=current_user.id,
            include_metadata=include_metadata,
            include_versions=include_versions,
            include_links=include_links,
            include_approvals=include_approvals
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{document_id}")
async def update_document(
    document_id: int,
    document: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update document fields"""
    try:
        service = DocumentService(db)
        result = service.update_document(
            document_id=document_id,
            user_id=current_user.id,
            title=document.title,
            description=document.description,
            purpose=document.purpose,
            scope=document.scope,
            category=document.category,
            standard=document.standard,
            department=document.department,
            tags=document.tags,
            keywords=document.keywords,
            metadata=document.metadata
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    reason: Optional[str] = Query(None, description="Reason for deletion"),
    permanent: bool = Query(False, description="Permanent delete (admin only)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a document"""
    try:
        service = DocumentService(db)
        result = service.delete_document(
            document_id=document_id,
            user_id=current_user.id,
            reason=reason,
            permanent=permanent
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/")
async def search_documents(
    query: Optional[str] = Query(None, description="Search query"),
    level: Optional[DocumentLevelEnum] = Query(None, description="Filter by level"),
    document_type: Optional[DocumentTypeEnum] = Query(None, description="Filter by type"),
    status_filter: Optional[DocumentStatusEnum] = Query(None, description="Filter by status", alias="status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    standard: Optional[StandardEnum] = Query(None, description="Filter by standard"),
    department: Optional[str] = Query(None, description="Filter by department"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search documents with filters"""
    try:
        service = DocumentService(db)
        result = service.search_documents(
            query=query,
            level=level,
            document_type=document_type,
            status=status_filter,
            category=category,
            standard=standard,
            department=department,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============= File Upload Endpoints =============

@router.post("/{document_id}/upload")
async def upload_document_file(
    document_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload file for a document"""
    try:
        # Read file stream
        contents = await file.read()
        file_stream = io.BytesIO(contents)

        service = DocumentService(db)
        result = service.upload_document_file(
            document_id=document_id,
            file_stream=file_stream,
            filename=file.filename,
            user_id=current_user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{document_id}/version")
async def create_new_version(
    document_id: int,
    change_summary: str = Query(..., description="Summary of changes"),
    change_reason: Optional[str] = Query(None, description="Reason for new version"),
    is_major_version: bool = Query(False, description="Is major version"),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new version of a document"""
    try:
        file_stream = None
        filename = None

        if file:
            contents = await file.read()
            file_stream = io.BytesIO(contents)
            filename = file.filename

        service = DocumentService(db)
        result = service.create_new_version(
            document_id=document_id,
            user_id=current_user.id,
            file_stream=file_stream,
            filename=filename,
            change_summary=change_summary,
            change_reason=change_reason,
            is_major_version=is_major_version
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============= Metadata Endpoints =============

@router.put("/{document_id}/metadata")
async def update_document_metadata(
    document_id: int,
    metadata: DocumentMetadataUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update extended document metadata"""
    try:
        service = DocumentService(db)
        result = service.update_document_metadata(
            document_id=document_id,
            user_id=current_user.id,
            **metadata.model_dump(exclude_unset=True)
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============= Workflow Endpoints =============

@router.post("/{document_id}/submit")
async def submit_for_review(
    document_id: int,
    workflow: WorkflowSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit document for review (Doer → Checker)"""
    try:
        service = DocumentService(db)
        result = service.workflow.submit_for_review(
            document_id=document_id,
            doer_id=current_user.id,
            checker_id=workflow.checker_id,
            comments=workflow.comments
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{document_id}/review")
async def review_document(
    document_id: int,
    review: WorkflowReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Review document (Checker reviews and approves/rejects)"""
    try:
        service = DocumentService(db)
        result = service.workflow.review_document(
            document_id=document_id,
            checker_id=current_user.id,
            action=review.action,
            approver_id=review.approver_id,
            comments=review.comments,
            signature=review.signature
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{document_id}/approve")
async def approve_document(
    document_id: int,
    approval: WorkflowApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Final approval of document (Approver approves/rejects)"""
    try:
        service = DocumentService(db)
        result = service.workflow.approve_document(
            document_id=document_id,
            approver_id=current_user.id,
            action=approval.action,
            comments=approval.comments,
            signature=approval.signature
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{document_id}/workflow/status")
async def get_workflow_status(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workflow status and participants"""
    try:
        service = DocumentService(db)
        result = service.workflow.get_workflow_status(document_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/pending/approvals")
async def get_pending_approvals(
    role: Optional[str] = Query(None, description="Filter by role (checker/approver)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get documents pending approval for current user"""
    try:
        service = DocumentService(db)
        result = service.workflow.get_pending_approvals(current_user.id, role)
        return {"pending_approvals": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============= Linking Endpoints =============

@router.post("/{document_id}/links")
async def create_document_link(
    document_id: int,
    link: DocumentLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a link between documents"""
    try:
        service = DocumentService(db)
        result = service.linking.create_link(
            source_document_id=document_id,
            target_document_id=link.target_document_id,
            link_type=link.link_type,
            description=link.description,
            is_bidirectional=link.is_bidirectional,
            strength=link.strength,
            user_id=current_user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{document_id}/links")
async def get_document_links(
    document_id: int,
    direction: str = Query("all", description="Link direction (outgoing/incoming/all)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all links for a document"""
    try:
        service = DocumentService(db)
        result = service.linking.get_document_links(document_id, direction)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{document_id}/hierarchy")
async def get_document_hierarchy(
    document_id: int,
    max_depth: int = Query(5, ge=1, le=10, description="Maximum depth to traverse"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document hierarchy (parent and children)"""
    try:
        service = DocumentService(db)
        result = service.linking.get_hierarchy(document_id, max_depth)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{document_id}/traceability")
async def get_traceability_matrix(
    document_id: int,
    depth: int = Query(2, ge=1, le=5, description="Depth to trace"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get traceability matrix showing all relationships"""
    try:
        service = DocumentService(db)
        result = service.linking.get_traceability_matrix(document_id, depth)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============= Template Endpoints =============

@router.post("/templates/index")
async def index_template(
    template: TemplateIndexCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Index a template for quick search"""
    try:
        service = DocumentService(db)
        result = service.template.index_template(**template.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/templates/auto-index")
async def auto_index_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Automatically index all Level 4 templates"""
    try:
        service = DocumentService(db)
        result = service.template.auto_index_templates()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/templates/search")
async def search_templates(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory"),
    is_dynamic: Optional[bool] = Query(None, description="Filter by dynamic flag"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search templates"""
    try:
        service = DocumentService(db)
        result = service.template.search_templates(query, category, subcategory, is_dynamic, limit)
        return {"templates": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/templates/{template_code}")
async def get_template_by_code(
    template_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get template by unique code"""
    try:
        service = DocumentService(db)
        result = service.template.get_template_by_code(template_code)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============= Access Control Endpoints =============

@router.post("/{document_id}/access/grant")
async def grant_document_access(
    document_id: int,
    access: AccessGrant,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Grant access to a document"""
    try:
        service = DocumentService(db)
        result = service.access_control.grant_access(
            document_id=document_id,
            user_id=access.user_id,
            role_id=access.role_id,
            department_id=access.department_id,
            can_view=access.can_view,
            can_edit=access.can_edit,
            can_review=access.can_review,
            can_approve=access.can_approve,
            can_delete=access.can_delete,
            valid_until=access.valid_until,
            granted_by=current_user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{document_id}/access")
async def get_document_access_list(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all access records for a document"""
    try:
        service = DocumentService(db)
        result = service.access_control.get_document_access_list(document_id)
        return {"access_list": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============= Retention Policy Endpoints =============

@router.post("/retention/policies")
async def create_retention_policy(
    policy: RetentionPolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a retention policy"""
    try:
        service = DocumentService(db)
        result = service.retention.create_retention_policy(**policy.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/retention/policies")
async def list_retention_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all retention policies"""
    try:
        service = DocumentService(db)
        result = service.retention.list_retention_policies()
        return {"policies": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{document_id}/retention/policy")
async def get_applicable_retention_policy(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get applicable retention policy for a document"""
    try:
        service = DocumentService(db)
        result = service.retention.get_applicable_policy(document_id)
        return result if result else {"message": "No applicable policy found"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{document_id}/archive")
async def archive_document(
    document_id: int,
    reason: Optional[str] = Query(None, description="Reason for archiving"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive a document"""
    try:
        service = DocumentService(db)
        result = service.retention.archive_document(document_id, current_user.id, reason)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/retention/review")
async def get_documents_for_retention_review(
    days_before_destruction: int = Query(90, ge=1, le=365, description="Days before destruction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get documents approaching destruction date for review"""
    try:
        service = DocumentService(db)
        result = service.retention.get_documents_for_review(days_before_destruction)
        return {"documents": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============= Numbering Endpoints =============

@router.get("/numbering/preview")
async def preview_next_document_number(
    level: DocumentLevelEnum = Query(..., description="Document level"),
    category: Optional[str] = Query(None, description="Document category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Preview the next document number"""
    try:
        service = DocumentService(db)
        next_number = service.numbering.get_next_number_preview(level, category)
        return {"next_number": next_number}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/numbering/status")
async def get_sequence_status(
    level: DocumentLevelEnum = Query(..., description="Document level"),
    category: Optional[str] = Query(None, description="Document category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current sequence status"""
    try:
        service = DocumentService(db)
        result = service.numbering.get_sequence_status(level, category)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
