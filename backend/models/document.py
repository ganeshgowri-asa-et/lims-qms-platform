"""
Document Management System models - Comprehensive implementation
Supports 5-level hierarchy, metadata tracking, workflow, versioning, and traceability
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, JSON, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel
import enum


class DocumentLevelEnum(str, enum.Enum):
    """Document hierarchy levels"""
    LEVEL_1 = "Level 1"  # Quality Manual, Policy, Vision & Mission
    LEVEL_2 = "Level 2"  # Quality System Procedures (ISO 17025/9001)
    LEVEL_3 = "Level 3"  # Operation & Test Procedures (PV Standards)
    LEVEL_4 = "Level 4"  # Templates, Formats, Checklists, Test Protocols
    LEVEL_5 = "Level 5"  # Records (generated from Level 4)


class DocumentStatusEnum(str, enum.Enum):
    """Document status in workflow"""
    DRAFT = "Draft"
    PENDING_REVIEW = "Pending Review"
    IN_REVIEW = "In Review"
    REVIEW_APPROVED = "Review Approved"
    PENDING_APPROVAL = "Pending Approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    OBSOLETE = "Obsolete"
    ARCHIVED = "Archived"
    SUPERSEDED = "Superseded"


class DocumentTypeEnum(str, enum.Enum):
    """Document types"""
    QUALITY_MANUAL = "Quality Manual"
    POLICY = "Policy"
    VISION_MISSION = "Vision & Mission"
    PROCEDURE = "Procedure"
    WORK_INSTRUCTION = "Work Instruction"
    FORM = "Form"
    TEMPLATE = "Template"
    CHECKLIST = "Checklist"
    TEST_PROTOCOL = "Test Protocol"
    RECORD = "Record"
    FLOWCHART = "Flowchart"
    INFOGRAPHIC = "Infographic"


class StandardEnum(str, enum.Enum):
    """Industry standards"""
    ISO_17025 = "ISO 17025"
    ISO_9001 = "ISO 9001"
    IEC_61215 = "IEC 61215"
    IEC_61730 = "IEC 61730"
    IEC_61853 = "IEC 61853"
    IEC_62804 = "IEC 62804"
    IEC_62716 = "IEC 62716"
    IEC_61701 = "IEC 61701"
    IEC_62332 = "IEC 62332"
    IEC_63202 = "IEC 63202"
    IEC_60904 = "IEC 60904"


class ApprovalActionEnum(str, enum.Enum):
    """Approval workflow actions"""
    SUBMITTED = "Submitted"
    REVIEWED = "Reviewed"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    REVISION_REQUESTED = "Revision Requested"
    WITHDRAWN = "Withdrawn"


class DocumentLevel(BaseModel):
    """Document Level configuration for numbering and hierarchy"""
    __tablename__ = 'document_levels'

    level_number = Column(Integer, nullable=False, unique=True, index=True)
    level_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    numbering_format = Column(String(200), nullable=True)  # e.g., "L{level}-{category}-{year}-{seq:04d}"
    auto_numbering = Column(Boolean, default=True, nullable=False)
    requires_approval = Column(Boolean, default=True, nullable=False)
    retention_years = Column(Integer, default=7, nullable=False)


class Document(BaseModel):
    """Main document model with comprehensive metadata"""
    __tablename__ = 'documents'

    # Core identifiers
    document_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    level = Column(Enum(DocumentLevelEnum), nullable=False, index=True)
    document_type = Column(Enum(DocumentTypeEnum), nullable=True, index=True)

    # Classification
    category = Column(String(100), nullable=True, index=True)  # Quality, Safety, Environmental
    standard = Column(Enum(StandardEnum), nullable=True, index=True)
    department = Column(String(100), nullable=True, index=True)
    process_area = Column(String(100), nullable=True)

    # Status and lifecycle
    status = Column(Enum(DocumentStatusEnum), default=DocumentStatusEnum.DRAFT, nullable=False, index=True)
    effective_date = Column(DateTime(timezone=True), nullable=True)
    review_date = Column(DateTime(timezone=True), nullable=True)
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    obsolete_date = Column(DateTime(timezone=True), nullable=True)

    # Content
    description = Column(Text, nullable=True)
    purpose = Column(Text, nullable=True)
    scope = Column(Text, nullable=True)

    # Version control
    current_version_id = Column(Integer, ForeignKey('document_versions.id'), nullable=True)
    version = Column(String(20), default="1.0", nullable=False)
    revision_number = Column(Integer, default=0, nullable=False)

    # File management
    file_path = Column(String(500), nullable=True)
    file_type = Column(String(50), nullable=True)
    file_size = Column(Integer, nullable=True)
    checksum = Column(String(64), nullable=True)

    # Hierarchy and relationships
    parent_document_id = Column(Integer, ForeignKey('documents.id'), nullable=True)
    supersedes_document_id = Column(Integer, ForeignKey('documents.id'), nullable=True)
    is_template = Column(Boolean, default=False, nullable=False, index=True)
    template_document_id = Column(Integer, ForeignKey('documents.id'), nullable=True)

    # Document owner
    document_owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Workflow - Doer-Checker-Approver
    doer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    checker_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    approver_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Workflow timestamps
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Tags and metadata
    tags = Column(JSON, nullable=True)  # ["calibration", "equipment", "quality"]
    keywords = Column(JSON, nullable=True)

    # Metadata JSON - extensible for custom fields
    metadata = Column(JSON, nullable=True)

    # Access control
    is_confidential = Column(Boolean, default=False, nullable=False)
    is_controlled = Column(Boolean, default=True, nullable=False)
    access_level = Column(String(50), default="internal", nullable=False)  # public, internal, confidential, restricted

    # Retention
    retention_years = Column(Integer, default=7, nullable=False)
    destruction_date = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    versions = relationship('DocumentVersion', back_populates='document', foreign_keys='DocumentVersion.document_id', cascade="all, delete-orphan")
    parent_document = relationship('Document', remote_side='Document.id', foreign_keys=[parent_document_id])
    supersedes_document = relationship('Document', remote_side='Document.id', foreign_keys=[supersedes_document_id])
    template_document = relationship('Document', remote_side='Document.id', foreign_keys=[template_document_id])
    metadata_detail = relationship('DocumentMetadata', back_populates='document', uselist=False, cascade="all, delete-orphan")
    approvals = relationship('DocumentApproval', back_populates='document', cascade="all, delete-orphan")
    links_from = relationship('DocumentLink', foreign_keys='DocumentLink.source_document_id', back_populates='source_document', cascade="all, delete-orphan")
    links_to = relationship('DocumentLink', foreign_keys='DocumentLink.target_document_id', back_populates='target_document', cascade="all, delete-orphan")
    access_controls = relationship('DocumentAccess', back_populates='document', cascade="all, delete-orphan")


class DocumentMetadata(BaseModel):
    """Extended metadata for documents"""
    __tablename__ = 'document_metadata'

    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, unique=True)

    # Table of contents
    table_of_contents = Column(JSON, nullable=True)  # [{section: "1", title: "Introduction", page: 1}]

    # Responsibilities
    responsibilities = Column(JSON, nullable=True)  # [{role: "Lab Manager", responsibility: "Approve calibration"}]

    # Equipment and resources
    equipment_required = Column(JSON, nullable=True)  # [{name: "Multimeter", spec: "±0.1%", standard: "IEC 61010"}]
    software_required = Column(JSON, nullable=True)  # [{name: "LabView", version: "2021", purpose: "Data acquisition"}]
    resources_required = Column(JSON, nullable=True)  # [{resource: "Clean room", specification: "Class 1000"}]

    # Process documentation
    process_flowchart = Column(Text, nullable=True)  # URL or base64 encoded image
    value_stream_map = Column(Text, nullable=True)
    turtle_diagram = Column(Text, nullable=True)
    infographics = Column(JSON, nullable=True)  # [{type: "process flow", url: "..."}]

    # KPIs and metrics
    kpi_definitions = Column(JSON, nullable=True)  # [{name: "Calibration uptime", target: "99%", frequency: "monthly"}]
    measurement_frequency = Column(String(100), nullable=True)

    # Annexures and references
    annexures = Column(JSON, nullable=True)  # [{title: "Annexure A", description: "...", file_path: "..."}]
    references = Column(JSON, nullable=True)  # [{title: "ISO 17025:2017", section: "5.6"}]

    # Risk and analysis
    risk_assessment = Column(JSON, nullable=True)  # [{risk: "Calibration drift", severity: "high", mitigation: "..."}]
    process_analysis = Column(Text, nullable=True)

    # Non-conformance control
    nc_control_procedure = Column(Text, nullable=True)
    nc_escalation_matrix = Column(JSON, nullable=True)

    # Training requirements
    training_required = Column(JSON, nullable=True)  # [{role: "Technician", training: "IEC 61215 basics", frequency: "annual"}]

    # Safety and compliance
    safety_requirements = Column(JSON, nullable=True)
    compliance_checklist = Column(JSON, nullable=True)

    # Custom fields (extensible)
    custom_fields = Column(JSON, nullable=True)

    # Relationship
    document = relationship('Document', back_populates='metadata_detail')


class DocumentVersion(BaseModel):
    """Document version history with complete audit trail"""
    __tablename__ = 'document_versions'

    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    version_number = Column(String(20), nullable=False)  # 1.0, 1.1, 2.0
    revision_number = Column(Integer, default=0, nullable=False)

    # Change tracking
    change_summary = Column(Text, nullable=True)
    change_details = Column(JSON, nullable=True)  # Detailed change log
    change_reason = Column(String(200), nullable=True)

    # File information
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(50), nullable=True)
    checksum = Column(String(64), nullable=True)  # SHA-256 hash

    # Release information
    released_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    released_at = Column(DateTime(timezone=True), nullable=True)
    effective_from = Column(DateTime(timezone=True), nullable=True)
    effective_until = Column(DateTime(timezone=True), nullable=True)

    # Status
    is_current = Column(Boolean, default=False, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    # Relationships
    document = relationship('Document', back_populates='versions', foreign_keys=[document_id])


class DocumentApproval(BaseModel):
    """Document approval workflow tracking"""
    __tablename__ = 'document_approvals'

    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    version_number = Column(String(20), nullable=False)

    # Approval role
    approval_role = Column(String(50), nullable=False)  # doer, checker, approver
    approver_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Action
    action = Column(Enum(ApprovalActionEnum), nullable=False)
    action_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Comments and feedback
    comments = Column(Text, nullable=True)
    attachments = Column(JSON, nullable=True)  # [{filename: "feedback.pdf", path: "..."}]

    # Digital signature
    signature = Column(Text, nullable=True)  # Digital signature or approval token
    ip_address = Column(String(45), nullable=True)

    # Sequence
    sequence_number = Column(Integer, default=0, nullable=False)  # Order of approvals

    # Relationship
    document = relationship('Document', back_populates='approvals')


class DocumentLink(BaseModel):
    """Bidirectional document linking for traceability"""
    __tablename__ = 'document_links'

    source_document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    target_document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)

    # Link metadata
    link_type = Column(String(50), nullable=False)  # parent-child, reference, related, supersedes, implements
    description = Column(Text, nullable=True)
    is_bidirectional = Column(Boolean, default=False, nullable=False)

    # Relationship strength
    strength = Column(String(20), default="normal", nullable=False)  # strong, normal, weak

    # Relationships
    source_document = relationship('Document', foreign_keys=[source_document_id], back_populates='links_from')
    target_document = relationship('Document', foreign_keys=[target_document_id], back_populates='links_to')


class DocumentAccess(BaseModel):
    """Document access control - who can view/edit/approve"""
    __tablename__ = 'document_access'

    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    role_id = Column(Integer, nullable=True, index=True)  # For role-based access
    department_id = Column(Integer, nullable=True, index=True)  # For department-based access

    # Permissions
    can_view = Column(Boolean, default=False, nullable=False)
    can_edit = Column(Boolean, default=False, nullable=False)
    can_review = Column(Boolean, default=False, nullable=False)
    can_approve = Column(Boolean, default=False, nullable=False)
    can_delete = Column(Boolean, default=False, nullable=False)

    # Access validity
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Relationship
    document = relationship('Document', back_populates='access_controls')


class TemplateIndex(BaseModel):
    """Dynamic template indexing for Level 4 templates"""
    __tablename__ = 'template_index'

    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)

    # Template metadata
    template_name = Column(String(200), nullable=False, index=True)
    template_code = Column(String(50), nullable=True, unique=True, index=True)
    category = Column(String(100), nullable=True, index=True)
    subcategory = Column(String(100), nullable=True)

    # Template properties
    is_dynamic = Column(Boolean, default=False, nullable=False)
    fields_schema = Column(JSON, nullable=True)  # JSON schema for template fields
    validation_rules = Column(JSON, nullable=True)

    # Usage tracking
    usage_count = Column(Integer, default=0, nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Auto-indexing
    auto_indexed = Column(Boolean, default=False, nullable=False)
    indexed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Search optimization
    search_keywords = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)


class DocumentRetentionPolicy(BaseModel):
    """Document retention policies by category/type"""
    __tablename__ = 'document_retention_policies'

    policy_name = Column(String(200), nullable=False, unique=True)
    document_level = Column(Enum(DocumentLevelEnum), nullable=True, index=True)
    document_type = Column(Enum(DocumentTypeEnum), nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)

    # Retention rules
    retention_years = Column(Integer, nullable=False)
    retention_months = Column(Integer, default=0, nullable=False)

    # Actions
    auto_archive = Column(Boolean, default=False, nullable=False)
    auto_destroy = Column(Boolean, default=False, nullable=False)
    require_approval_for_destruction = Column(Boolean, default=True, nullable=False)

    # Legal and compliance
    legal_requirement = Column(Boolean, default=False, nullable=False)
    regulation_reference = Column(String(200), nullable=True)

    # Description
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)


class DocumentNumberSequence(BaseModel):
    """Document numbering sequence tracker"""
    __tablename__ = 'document_number_sequences'

    level = Column(Enum(DocumentLevelEnum), nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    year = Column(Integer, nullable=False, index=True)

    # Sequence
    current_sequence = Column(Integer, default=0, nullable=False)
    prefix = Column(String(50), nullable=True)
    suffix = Column(String(50), nullable=True)

    # Format
    format_template = Column(String(200), nullable=True)

    # Unique constraint
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class DocumentAuditLog(BaseModel):
    """Comprehensive audit trail for all document operations"""
    __tablename__ = 'document_audit_log'

    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)

    # Action details
    action = Column(String(100), nullable=False, index=True)  # created, updated, viewed, approved, etc.
    action_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Change tracking
    field_name = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)

    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    session_id = Column(String(100), nullable=True)

    # Additional data
    metadata = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
