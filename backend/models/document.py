"""
Document Management System models
Enhanced for comprehensive template and document management
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, JSON, Float, Date, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class DocumentLevelEnum(str, enum.Enum):
    """Document hierarchy levels"""
    LEVEL_1 = "Level 1"  # Quality Manual, Policy
    LEVEL_2 = "Level 2"  # Quality System Procedures
    LEVEL_3 = "Level 3"  # Operation & Test Procedures
    LEVEL_4 = "Level 4"  # Templates, Formats, Checklists
    LEVEL_5 = "Level 5"  # Records


class DocumentStatusEnum(str, enum.Enum):
    """Document status"""
    DRAFT = "Draft"
    IN_REVIEW = "In Review"
    APPROVED = "Approved"
    OBSOLETE = "Obsolete"
    ARCHIVED = "Archived"


class DocumentTypeEnum(str, enum.Enum):
    """Document type categories"""
    QUALITY_MANUAL = "Quality Manual"
    POLICY = "Policy"
    PROCEDURE = "Procedure"
    WORK_INSTRUCTION = "Work Instruction"
    FORM = "Form"
    TEMPLATE = "Template"
    CHECKLIST = "Checklist"
    TEST_PROTOCOL = "Test Protocol"
    RECORD = "Record"
    SPECIFICATION = "Specification"
    REPORT = "Report"
    FLOWCHART = "Flowchart"
    OTHER = "Other"


class ISOStandardEnum(str, enum.Enum):
    """ISO and other standards"""
    ISO_17025 = "ISO/IEC 17025"
    ISO_9001 = "ISO 9001"
    ISO_14001 = "ISO 14001"
    ISO_45001 = "ISO 45001"
    IEC_61215 = "IEC 61215"
    IEC_61730 = "IEC 61730"
    IEC_62804 = "IEC 62804"
    IEC_61853 = "IEC 61853"
    OTHER = "Other"


class RetentionPolicyEnum(str, enum.Enum):
    """Document retention policies"""
    PERMANENT = "Permanent"
    SEVEN_YEARS = "7 Years"
    FIVE_YEARS = "5 Years"
    THREE_YEARS = "3 Years"
    ONE_YEAR = "1 Year"
    UNTIL_SUPERSEDED = "Until Superseded"


class DocumentLevel(BaseModel):
    """Document Level configuration"""
    __tablename__ = 'document_levels'

    level_number = Column(Integer, nullable=False, unique=True)
    level_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    numbering_format = Column(String(100), nullable=True)  # e.g., "L1-{year}-{seq:04d}"


class Document(BaseModel):
    """Enhanced Document model with comprehensive metadata"""
    __tablename__ = 'documents'

    # Core identification
    document_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    level = Column(Enum(DocumentLevelEnum), nullable=False, index=True)
    document_type = Column(Enum(DocumentTypeEnum), nullable=True, index=True)

    # Standards and categorization
    category = Column(String(100), nullable=True, index=True)  # Department/Process category
    iso_standard = Column(Enum(ISOStandardEnum), nullable=True, index=True)
    standard_clause = Column(String(100), nullable=True)  # e.g., "6.2", "7.1.3"
    pv_standard = Column(String(100), nullable=True)  # IEC 61215, 61730, etc.

    # Document information
    status = Column(Enum(DocumentStatusEnum), default=DocumentStatusEnum.DRAFT, nullable=False, index=True)
    description = Column(Text, nullable=True)
    purpose = Column(Text, nullable=True)
    scope = Column(Text, nullable=True)

    # File management
    current_version_id = Column(Integer, ForeignKey('document_versions.id'), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_type = Column(String(50), nullable=True)
    file_size = Column(Integer, nullable=True)  # bytes

    # Hierarchy and linking
    parent_document_id = Column(Integer, ForeignKey('documents.id'), nullable=True, index=True)

    # Ownership and responsibility
    document_owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    department = Column(String(100), nullable=True, index=True)
    process_owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Workflow fields
    doer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    checker_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    approver_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    reviewed_at = Column(String(255), nullable=True)
    approved_at = Column(String(255), nullable=True)

    # Document lifecycle
    effective_date = Column(Date, nullable=True)
    review_date = Column(Date, nullable=True)
    next_review_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    retention_policy = Column(Enum(RetentionPolicyEnum), default=RetentionPolicyEnum.PERMANENT)

    # Review cycle
    review_frequency_months = Column(Integer, nullable=True)  # e.g., 12, 24, 36

    # Tagging and search
    tags = Column(JSON, nullable=True)  # ["calibration", "equipment", "quality"]
    keywords = Column(JSON, nullable=True)  # Additional searchable keywords

    # Template-specific fields (for Level 4 documents)
    is_template = Column(Boolean, default=False)
    template_category_id = Column(Integer, ForeignKey('template_categories.id'), nullable=True)

    # Additional metadata (extensible JSON field)
    metadata = Column(JSON, nullable=True)
    # Can store: custom fields, infographics data, process maps, etc.

    # Relationships
    versions = relationship('DocumentVersion', back_populates='document', foreign_keys='DocumentVersion.document_id')
    parent_document = relationship('Document', remote_side='Document.id', foreign_keys=[parent_document_id])
    template_category = relationship('TemplateCategory', back_populates='documents')

    # Metadata relationships
    table_of_contents = relationship('DocumentTableOfContents', back_populates='document', cascade='all, delete-orphan')
    responsibilities = relationship('DocumentResponsibility', back_populates='document', cascade='all, delete-orphan')
    equipment_list = relationship('DocumentEquipment', back_populates='document', cascade='all, delete-orphan')
    kpis = relationship('DocumentKPI', back_populates='document', cascade='all, delete-orphan')
    flowcharts = relationship('DocumentFlowchart', back_populates='document', cascade='all, delete-orphan')
    links_as_parent = relationship('DocumentLink', back_populates='parent_document', foreign_keys='DocumentLink.parent_document_id')
    links_as_child = relationship('DocumentLink', back_populates='child_document', foreign_keys='DocumentLink.child_document_id')


class DocumentVersion(BaseModel):
    """Enhanced Document version history with retention policies"""
    __tablename__ = 'document_versions'

    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    version_number = Column(String(20), nullable=False, index=True)  # 1.0, 1.1, 2.0
    revision_number = Column(Integer, default=0)
    change_summary = Column(Text, nullable=True)
    change_type = Column(String(50), nullable=True)  # Minor, Major, Editorial
    change_reason = Column(Text, nullable=True)

    # File information
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    checksum = Column(String(64), nullable=True)  # SHA-256 hash

    # Release information
    released_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    released_at = Column(String(255), nullable=True)
    effective_date = Column(Date, nullable=True)

    # Retention
    retention_until = Column(Date, nullable=True)  # Calculated based on retention policy

    # Approval information
    approved_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved_at = Column(String(255), nullable=True)

    # Version status
    is_current = Column(Boolean, default=False)  # Only one version should be current
    is_obsolete = Column(Boolean, default=False)

    # Relationships
    document = relationship('Document', back_populates='versions', foreign_keys=[document_id])


# ==================== TEMPLATE MANAGEMENT ====================

class TemplateCategory(BaseModel):
    """Template categorization for Level 4 documents"""
    __tablename__ = 'template_categories'

    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    parent_category_id = Column(Integer, ForeignKey('template_categories.id'), nullable=True)
    icon = Column(String(100), nullable=True)  # Icon identifier for UI
    color_code = Column(String(7), nullable=True)  # Hex color code
    sort_order = Column(Integer, default=0)

    # Categorization metadata
    iso_standard = Column(Enum(ISOStandardEnum), nullable=True)
    department = Column(String(100), nullable=True)
    process_area = Column(String(100), nullable=True)

    # Relationships
    parent_category = relationship('TemplateCategory', remote_side='TemplateCategory.id', foreign_keys=[parent_category_id])
    documents = relationship('Document', back_populates='template_category')


# ==================== DOCUMENT LINKING & TRACEABILITY ====================

class DocumentLink(BaseModel):
    """Bi-directional document linking for traceability"""
    __tablename__ = 'document_links'

    parent_document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    child_document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)

    # Link metadata
    link_type = Column(String(50), nullable=True)  # "derives_from", "references", "implements", "supports"
    description = Column(Text, nullable=True)
    section_reference = Column(String(100), nullable=True)  # e.g., "Section 5.2", "Clause 7.1"

    # Traceability information
    traceability_level = Column(String(50), nullable=True)  # "direct", "indirect"
    compliance_reference = Column(String(200), nullable=True)  # ISO clause reference

    # Relationships
    parent_document = relationship('Document', back_populates='links_as_parent', foreign_keys=[parent_document_id])
    child_document = relationship('Document', back_populates='links_as_child', foreign_keys=[child_document_id])


# ==================== DOCUMENT METADATA ====================

class DocumentTableOfContents(BaseModel):
    """Table of Contents for documents"""
    __tablename__ = 'document_table_of_contents'

    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    section_number = Column(String(20), nullable=False)  # e.g., "1", "1.1", "2.3.4"
    section_title = Column(String(500), nullable=False)
    page_number = Column(Integer, nullable=True)
    level = Column(Integer, default=1)  # Heading level (1, 2, 3, etc.)
    parent_section_id = Column(Integer, ForeignKey('document_table_of_contents.id'), nullable=True)
    sort_order = Column(Integer, default=0)

    # Relationships
    document = relationship('Document', back_populates='table_of_contents')
    parent_section = relationship('DocumentTableOfContents', remote_side='DocumentTableOfContents.id', foreign_keys=[parent_section_id])


class DocumentResponsibility(BaseModel):
    """Responsibility matrix for documents"""
    __tablename__ = 'document_responsibilities'

    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    role_title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Responsibility flags
    is_responsible = Column(Boolean, default=False)  # R - Responsible (doer)
    is_accountable = Column(Boolean, default=False)  # A - Accountable (owner)
    is_consulted = Column(Boolean, default=False)    # C - Consulted
    is_informed = Column(Boolean, default=False)     # I - Informed

    # User assignment (optional)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    department = Column(String(100), nullable=True)

    # Additional details
    tasks = Column(JSON, nullable=True)  # List of specific tasks
    authority_level = Column(String(100), nullable=True)

    # Relationships
    document = relationship('Document', back_populates='responsibilities')


class DocumentEquipment(BaseModel):
    """Equipment, software, accessories, and resources for documents"""
    __tablename__ = 'document_equipment'

    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)

    # Equipment details
    name = Column(String(300), nullable=False)
    equipment_type = Column(String(100), nullable=True)  # "Equipment", "Software", "Accessory", "Resource"
    model = Column(String(200), nullable=True)
    manufacturer = Column(String(200), nullable=True)
    serial_number = Column(String(100), nullable=True)

    # Specifications
    specifications = Column(Text, nullable=True)
    calibration_required = Column(Boolean, default=False)
    calibration_frequency = Column(String(100), nullable=True)  # e.g., "Annual", "6 months"

    # Status
    status = Column(String(50), nullable=True)  # "Available", "In Use", "Under Maintenance", "Calibration Due"
    location = Column(String(200), nullable=True)

    # Additional information
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    document = relationship('Document', back_populates='equipment_list')


class DocumentKPI(BaseModel):
    """Key Performance Indicators for documents"""
    __tablename__ = 'document_kpis'

    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)

    # KPI details
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # "Quality", "Efficiency", "Compliance", "Safety"

    # Measurement
    metric = Column(String(200), nullable=False)  # What is measured
    unit_of_measure = Column(String(50), nullable=True)  # "percentage", "count", "days", "hours"
    target_value = Column(Float, nullable=True)
    threshold_min = Column(Float, nullable=True)
    threshold_max = Column(Float, nullable=True)

    # Frequency and responsibility
    measurement_frequency = Column(String(100), nullable=True)  # "Daily", "Weekly", "Monthly", "Quarterly"
    responsible_role = Column(String(200), nullable=True)
    responsible_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Analysis and reporting
    analysis_method = Column(Text, nullable=True)
    reporting_format = Column(String(100), nullable=True)  # "Chart", "Table", "Dashboard"

    # Additional information
    metadata = Column(JSON, nullable=True)

    # Relationships
    document = relationship('Document', back_populates='kpis')


class DocumentFlowchart(BaseModel):
    """Process flowcharts, value stream maps, and infographics"""
    __tablename__ = 'document_flowcharts'

    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)

    # Flowchart details
    title = Column(String(300), nullable=False)
    flowchart_type = Column(String(100), nullable=True)  # "Process Flow", "Value Stream Map", "Turtle Diagram", "SIPOC"
    description = Column(Text, nullable=True)

    # File information
    file_path = Column(String(500), nullable=True)  # Path to flowchart image/file
    file_type = Column(String(50), nullable=True)  # "png", "svg", "pdf", "vsd"

    # Flowchart data (for interactive/editable flowcharts)
    flowchart_data = Column(JSON, nullable=True)  # Structured data (nodes, edges, etc.)

    # Visual properties
    thumbnail_path = Column(String(500), nullable=True)
    page_number = Column(Integer, nullable=True)  # If in document

    # Additional metadata
    process_steps = Column(JSON, nullable=True)  # List of process steps
    decision_points = Column(JSON, nullable=True)  # List of decision points
    risks = Column(JSON, nullable=True)  # Associated risks
    controls = Column(JSON, nullable=True)  # Control measures

    # Relationships
    document = relationship('Document', back_populates='flowcharts')


# ==================== DOCUMENT NUMBERING ====================

class DocumentNumberingSequence(BaseModel):
    """Manages document numbering sequences"""
    __tablename__ = 'document_numbering_sequences'

    level = Column(Enum(DocumentLevelEnum), nullable=False, index=True)
    document_type = Column(Enum(DocumentTypeEnum), nullable=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    department = Column(String(100), nullable=True, index=True)

    # Sequence information
    current_sequence = Column(Integer, default=0, nullable=False)
    prefix = Column(String(20), nullable=True)  # e.g., "QM", "PROC", "FORM"
    format_template = Column(String(100), nullable=True)  # e.g., "{prefix}-{year}-{seq:04d}"

    # Constraints
    max_sequence = Column(Integer, nullable=True)  # Optional limit

    # Metadata
    last_generated_number = Column(String(100), nullable=True)
    last_generated_at = Column(String(255), nullable=True)
