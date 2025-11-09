"""
Enhanced Document and Template Management API endpoints
Comprehensive document lifecycle, template repository, and metadata management
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from backend.core import get_db
from backend.models.document import (
    Document, DocumentVersion, DocumentLink, DocumentTableOfContents,
    DocumentResponsibility, DocumentEquipment, DocumentKPI, DocumentFlowchart,
    TemplateCategory, DocumentNumberingSequence,
    DocumentLevelEnum, DocumentStatusEnum, DocumentTypeEnum, ISOStandardEnum, RetentionPolicyEnum
)
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from backend.services.document_service import (
    DocumentNumberingService, DocumentVersionService, DocumentLinkingService,
    DocumentLifecycleService, TemplateIndexingService
)
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import os
import shutil
from pathlib import Path

router = APIRouter()

# ==================== PYDANTIC SCHEMAS ====================

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    level: DocumentLevelEnum
    document_type: Optional[DocumentTypeEnum] = None
    category: Optional[str] = None
    iso_standard: Optional[ISOStandardEnum] = None
    standard_clause: Optional[str] = None
    pv_standard: Optional[str] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    scope: Optional[str] = None
    department: Optional[str] = None
    parent_document_id: Optional[int] = None
    review_frequency_months: Optional[int] = None
    retention_policy: Optional[RetentionPolicyEnum] = RetentionPolicyEnum.PERMANENT
    tags: Optional[List[str]] = []
    keywords: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    scope: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    id: int
    uuid: str
    document_number: str
    title: str
    level: str
    document_type: Optional[str]
    status: str
    category: Optional[str]
    iso_standard: Optional[str]
    department: Optional[str]
    is_template: bool
    current_version_id: Optional[int]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class DocumentDetailResponse(BaseModel):
    id: int
    uuid: str
    document_number: str
    title: str
    level: str
    document_type: Optional[str]
    status: str
    description: Optional[str]
    purpose: Optional[str]
    scope: Optional[str]
    category: Optional[str]
    iso_standard: Optional[str]
    standard_clause: Optional[str]
    pv_standard: Optional[str]
    department: Optional[str]
    document_owner_id: Optional[int]
    process_owner_id: Optional[int]
    doer_id: Optional[int]
    checker_id: Optional[int]
    approver_id: Optional[int]
    reviewed_at: Optional[str]
    approved_at: Optional[str]
    effective_date: Optional[str]
    review_date: Optional[str]
    next_review_date: Optional[str]
    retention_policy: Optional[str]
    review_frequency_months: Optional[int]
    is_template: bool
    template_category_id: Optional[int]
    tags: Optional[List[str]]
    keywords: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]
    file_path: Optional[str]
    file_type: Optional[str]
    file_size: Optional[int]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class VersionCreate(BaseModel):
    change_summary: str = Field(..., min_length=1)
    change_type: str = Field(default="Minor", pattern="^(Minor|Major|Editorial)$")
    change_reason: Optional[str] = None


class VersionResponse(BaseModel):
    id: int
    document_id: int
    version_number: str
    revision_number: int
    change_summary: str
    change_type: Optional[str]
    released_at: Optional[str]
    is_current: bool

    class Config:
        from_attributes = True


class DocumentLinkCreate(BaseModel):
    parent_document_id: int
    child_document_id: int
    link_type: str = "references"
    description: Optional[str] = None
    section_reference: Optional[str] = None
    compliance_reference: Optional[str] = None


class DocumentLinkResponse(BaseModel):
    id: int
    parent_document_id: int
    child_document_id: int
    link_type: str
    description: Optional[str]
    section_reference: Optional[str]

    class Config:
        from_attributes = True


class TOCCreate(BaseModel):
    section_number: str
    section_title: str
    page_number: Optional[int] = None
    level: int = 1
    parent_section_id: Optional[int] = None


class TOCResponse(BaseModel):
    id: int
    section_number: str
    section_title: str
    page_number: Optional[int]
    level: int

    class Config:
        from_attributes = True


class ResponsibilityCreate(BaseModel):
    role_title: str
    description: Optional[str] = None
    is_responsible: bool = False
    is_accountable: bool = False
    is_consulted: bool = False
    is_informed: bool = False
    user_id: Optional[int] = None
    department: Optional[str] = None
    tasks: Optional[List[str]] = []


class ResponsibilityResponse(BaseModel):
    id: int
    role_title: str
    is_responsible: bool
    is_accountable: bool
    is_consulted: bool
    is_informed: bool
    user_id: Optional[int]
    department: Optional[str]

    class Config:
        from_attributes = True


class EquipmentCreate(BaseModel):
    name: str
    equipment_type: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    specifications: Optional[str] = None
    calibration_required: bool = False


class EquipmentResponse(BaseModel):
    id: int
    name: str
    equipment_type: Optional[str]
    model: Optional[str]
    manufacturer: Optional[str]
    calibration_required: bool

    class Config:
        from_attributes = True


class KPICreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    metric: str
    unit_of_measure: Optional[str] = None
    target_value: Optional[float] = None
    measurement_frequency: Optional[str] = None


class KPIResponse(BaseModel):
    id: int
    name: str
    metric: str
    target_value: Optional[float]
    measurement_frequency: Optional[str]

    class Config:
        from_attributes = True


class FlowchartCreate(BaseModel):
    title: str
    flowchart_type: Optional[str] = None
    description: Optional[str] = None
    flowchart_data: Optional[Dict[str, Any]] = None


class FlowchartResponse(BaseModel):
    id: int
    title: str
    flowchart_type: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True


class TemplateCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    iso_standard: Optional[ISOStandardEnum] = None
    department: Optional[str] = None
    process_area: Optional[str] = None


class TemplateCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    parent_category_id: Optional[int]
    iso_standard: Optional[str]
    department: Optional[str]

    class Config:
        from_attributes = True


class TemplateIndexRequest(BaseModel):
    category_name: str
    tags: List[str] = []
    keywords: List[str] = []
    metadata: Optional[Dict[str, Any]] = {}


class BulkTemplateIndexRequest(BaseModel):
    templates: List[Dict[str, Any]]


# ==================== DOCUMENT CRUD ENDPOINTS ====================

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new document with auto-generated document number"""

    # Generate document number
    document_number = DocumentNumberingService.generate_document_number(
        db=db,
        level=document.level,
        document_type=document.document_type,
        department=document.department
    )

    new_document = Document(
        document_number=document_number,
        title=document.title,
        level=document.level,
        document_type=document.document_type,
        category=document.category,
        iso_standard=document.iso_standard,
        standard_clause=document.standard_clause,
        pv_standard=document.pv_standard,
        description=document.description,
        purpose=document.purpose,
        scope=document.scope,
        department=document.department,
        parent_document_id=document.parent_document_id,
        review_frequency_months=document.review_frequency_months,
        retention_policy=document.retention_policy,
        tags=document.tags,
        keywords=document.keywords,
        metadata=document.metadata,
        status=DocumentStatusEnum.DRAFT,
        doer_id=current_user.id,
        document_owner_id=current_user.id,
        created_by_id=current_user.id
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    level: Optional[DocumentLevelEnum] = None,
    status: Optional[DocumentStatusEnum] = None,
    document_type: Optional[DocumentTypeEnum] = None,
    iso_standard: Optional[ISOStandardEnum] = None,
    department: Optional[str] = None,
    is_template: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List documents with advanced filtering"""

    filters = [Document.is_deleted == False]

    if level:
        filters.append(Document.level == level)
    if status:
        filters.append(Document.status == status)
    if document_type:
        filters.append(Document.document_type == document_type)
    if iso_standard:
        filters.append(Document.iso_standard == iso_standard)
    if department:
        filters.append(Document.department == department)
    if is_template is not None:
        filters.append(Document.is_template == is_template)

    if search:
        search_filter = or_(
            Document.title.ilike(f"%{search}%"),
            Document.document_number.ilike(f"%{search}%"),
            Document.description.ilike(f"%{search}%")
        )
        filters.append(search_filter)

    documents = db.query(Document).filter(and_(*filters)).offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document by ID with full details"""

    document = db.query(Document).filter(
        and_(
            Document.id == document_id,
            Document.is_deleted == False
        )
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update document details"""

    document = db.query(Document).filter(
        and_(
            Document.id == document_id,
            Document.is_deleted == False
        )
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Update fields
    update_data = document_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)

    document.updated_by_id = current_user.id

    db.commit()
    db.refresh(document)

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a document"""

    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    document.is_deleted = True
    document.updated_by_id = current_user.id

    db.commit()


# ==================== DOCUMENT LIFECYCLE ENDPOINTS ====================

@router.put("/{document_id}/submit-review", response_model=DocumentResponse)
async def submit_for_review(
    document_id: int,
    checker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit document for review"""

    try:
        document = DocumentLifecycleService.submit_for_review(
            db=db,
            document_id=document_id,
            checker_id=checker_id
        )
        return document
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{document_id}/approve", response_model=DocumentResponse)
async def approve_document(
    document_id: int,
    effective_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a document"""

    try:
        document = DocumentLifecycleService.approve_document(
            db=db,
            document_id=document_id,
            approver_id=current_user.id,
            effective_date=effective_date
        )
        return document
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{document_id}/obsolete", response_model=DocumentResponse)
async def mark_obsolete(
    document_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark document as obsolete"""

    try:
        document = DocumentLifecycleService.mark_obsolete(
            db=db,
            document_id=document_id,
            reason=reason
        )
        return document
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{document_id}/archive", response_model=DocumentResponse)
async def archive_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive a document"""

    try:
        document = DocumentLifecycleService.archive_document(
            db=db,
            document_id=document_id
        )
        return document
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==================== VERSION CONTROL ENDPOINTS ====================

@router.post("/{document_id}/versions", response_model=VersionResponse, status_code=status.HTTP_201_CREATED)
async def create_document_version(
    document_id: int,
    version_data: VersionCreate,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new version of a document"""

    # Check if document exists
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Save uploaded file
    upload_dir = Path("uploads/documents")
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_extension = Path(file.filename).suffix
    file_name = f"{document.document_number}_v{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"
    file_path = upload_dir / file_name

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create version
    version = DocumentVersionService.create_version(
        db=db,
        document_id=document_id,
        file_path=str(file_path),
        change_summary=version_data.change_summary,
        change_type=version_data.change_type,
        change_reason=version_data.change_reason,
        released_by_id=current_user.id
    )

    # Update document file path
    document.file_path = str(file_path)
    document.file_type = file_extension.lstrip('.')
    db.commit()

    return version


@router.get("/{document_id}/versions", response_model=List[VersionResponse])
async def list_document_versions(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all versions of a document"""

    versions = db.query(DocumentVersion).filter(
        and_(
            DocumentVersion.document_id == document_id,
            DocumentVersion.is_deleted == False
        )
    ).order_by(DocumentVersion.revision_number.desc()).all()

    return versions


# ==================== DOCUMENT LINKING & TRACEABILITY ====================

@router.post("/links", response_model=DocumentLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_document_link(
    link_data: DocumentLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a link between documents"""

    link = DocumentLinkingService.create_link(
        db=db,
        parent_document_id=link_data.parent_document_id,
        child_document_id=link_data.child_document_id,
        link_type=link_data.link_type,
        description=link_data.description,
        section_reference=link_data.section_reference,
        compliance_reference=link_data.compliance_reference
    )

    return link


@router.get("/{document_id}/hierarchy")
async def get_document_hierarchy(
    document_id: int,
    direction: str = Query("both", regex="^(up|down|both)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document hierarchy (bi-directional traceability)"""

    hierarchy = DocumentLinkingService.get_document_hierarchy(
        db=db,
        document_id=document_id,
        direction=direction
    )

    return hierarchy


@router.get("/{document_id}/links", response_model=List[DocumentLinkResponse])
async def get_document_links(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all links for a document"""

    links = db.query(DocumentLink).filter(
        or_(
            DocumentLink.parent_document_id == document_id,
            DocumentLink.child_document_id == document_id
        ),
        DocumentLink.is_deleted == False
    ).all()

    return links


# ==================== DOCUMENT METADATA ENDPOINTS ====================

@router.post("/{document_id}/toc", response_model=TOCResponse, status_code=status.HTTP_201_CREATED)
async def add_table_of_contents(
    document_id: int,
    toc_data: TOCCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add table of contents entry"""

    toc = DocumentTableOfContents(
        document_id=document_id,
        **toc_data.dict()
    )

    db.add(toc)
    db.commit()
    db.refresh(toc)

    return toc


@router.get("/{document_id}/toc", response_model=List[TOCResponse])
async def get_table_of_contents(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get table of contents for a document"""

    toc_entries = db.query(DocumentTableOfContents).filter(
        and_(
            DocumentTableOfContents.document_id == document_id,
            DocumentTableOfContents.is_deleted == False
        )
    ).order_by(DocumentTableOfContents.sort_order).all()

    return toc_entries


@router.post("/{document_id}/responsibilities", response_model=ResponsibilityResponse, status_code=status.HTTP_201_CREATED)
async def add_responsibility(
    document_id: int,
    responsibility_data: ResponsibilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add responsibility entry"""

    responsibility = DocumentResponsibility(
        document_id=document_id,
        **responsibility_data.dict()
    )

    db.add(responsibility)
    db.commit()
    db.refresh(responsibility)

    return responsibility


@router.get("/{document_id}/responsibilities", response_model=List[ResponsibilityResponse])
async def get_responsibilities(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get responsibilities for a document"""

    responsibilities = db.query(DocumentResponsibility).filter(
        and_(
            DocumentResponsibility.document_id == document_id,
            DocumentResponsibility.is_deleted == False
        )
    ).all()

    return responsibilities


@router.post("/{document_id}/equipment", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def add_equipment(
    document_id: int,
    equipment_data: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add equipment entry"""

    equipment = DocumentEquipment(
        document_id=document_id,
        **equipment_data.dict()
    )

    db.add(equipment)
    db.commit()
    db.refresh(equipment)

    return equipment


@router.get("/{document_id}/equipment", response_model=List[EquipmentResponse])
async def get_equipment(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get equipment list for a document"""

    equipment_list = db.query(DocumentEquipment).filter(
        and_(
            DocumentEquipment.document_id == document_id,
            DocumentEquipment.is_deleted == False
        )
    ).all()

    return equipment_list


@router.post("/{document_id}/kpis", response_model=KPIResponse, status_code=status.HTTP_201_CREATED)
async def add_kpi(
    document_id: int,
    kpi_data: KPICreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add KPI entry"""

    kpi = DocumentKPI(
        document_id=document_id,
        **kpi_data.dict()
    )

    db.add(kpi)
    db.commit()
    db.refresh(kpi)

    return kpi


@router.get("/{document_id}/kpis", response_model=List[KPIResponse])
async def get_kpis(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get KPIs for a document"""

    kpis = db.query(DocumentKPI).filter(
        and_(
            DocumentKPI.document_id == document_id,
            DocumentKPI.is_deleted == False
        )
    ).all()

    return kpis


@router.post("/{document_id}/flowcharts", response_model=FlowchartResponse, status_code=status.HTTP_201_CREATED)
async def add_flowchart(
    document_id: int,
    flowchart_data: FlowchartCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add flowchart entry"""

    flowchart = DocumentFlowchart(
        document_id=document_id,
        **flowchart_data.dict()
    )

    db.add(flowchart)
    db.commit()
    db.refresh(flowchart)

    return flowchart


@router.get("/{document_id}/flowcharts", response_model=List[FlowchartResponse])
async def get_flowcharts(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get flowcharts for a document"""

    flowcharts = db.query(DocumentFlowchart).filter(
        and_(
            DocumentFlowchart.document_id == document_id,
            DocumentFlowchart.is_deleted == False
        )
    ).all()

    return flowcharts


# ==================== TEMPLATE MANAGEMENT ENDPOINTS ====================

@router.post("/templates/categories", response_model=TemplateCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_template_category(
    category_data: TemplateCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new template category"""

    category = TemplateCategory(**category_data.dict())

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.get("/templates/categories", response_model=List[TemplateCategoryResponse])
async def list_template_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all template categories"""

    categories = db.query(TemplateCategory).filter(
        TemplateCategory.is_deleted == False
    ).order_by(TemplateCategory.sort_order).all()

    return categories


@router.post("/{document_id}/index-template", response_model=DocumentResponse)
async def index_template(
    document_id: int,
    index_data: TemplateIndexRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Index a document as a template"""

    try:
        template = TemplateIndexingService.index_template(
            db=db,
            document_id=document_id,
            category_name=index_data.category_name,
            tags=index_data.tags,
            keywords=index_data.keywords,
            metadata=index_data.metadata
        )
        return template
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/templates/bulk-index")
async def bulk_index_templates(
    bulk_data: BulkTemplateIndexRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk index multiple templates"""

    indexed_templates = TemplateIndexingService.bulk_index_templates(
        db=db,
        templates_data=bulk_data.templates
    )

    return {
        "success": len(indexed_templates),
        "total": len(bulk_data.templates),
        "indexed_templates": [t.id for t in indexed_templates]
    }


@router.get("/templates/search", response_model=List[DocumentResponse])
async def search_templates(
    query: Optional[str] = None,
    category_id: Optional[int] = None,
    iso_standard: Optional[ISOStandardEnum] = None,
    department: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Advanced search for templates"""

    tag_list = tags.split(",") if tags else None

    templates = TemplateIndexingService.search_templates(
        db=db,
        query=query,
        category_id=category_id,
        iso_standard=iso_standard,
        department=department,
        tags=tag_list
    )

    return templates
