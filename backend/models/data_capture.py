"""
Data Capture & Filling Engine - Enhanced Models
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, JSON, Enum, Float
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class RecordStatusEnum(str, enum.Enum):
    """Enhanced record status for workflow"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUIRED = "revision_required"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class WorkflowActionEnum(str, enum.Enum):
    """Workflow actions"""
    SUBMIT = "submit"
    REVIEW = "review"
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_REVISION = "request_revision"
    REVISE = "revise"
    CANCEL = "cancel"
    ARCHIVE = "archive"


class ValidationSeverityEnum(str, enum.Enum):
    """Validation issue severity"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class BulkUploadStatusEnum(str, enum.Enum):
    """Bulk upload processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class FormWorkflowEvent(BaseModel):
    """Track all workflow transitions and actions"""
    __tablename__ = 'form_workflow_events'

    record_id = Column(Integer, ForeignKey('form_records.id', ondelete='CASCADE'), nullable=False)
    action = Column(Enum(WorkflowActionEnum), nullable=False)
    from_status = Column(Enum(RecordStatusEnum), nullable=True)
    to_status = Column(Enum(RecordStatusEnum), nullable=False)
    actor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    comments = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Relationships
    actor = relationship('User', foreign_keys=[actor_id])


class FormComment(BaseModel):
    """Comments and feedback on form records"""
    __tablename__ = 'form_comments'

    record_id = Column(Integer, ForeignKey('form_records.id', ondelete='CASCADE'), nullable=False)
    field_id = Column(Integer, ForeignKey('form_fields.id'), nullable=True)  # Comment on specific field
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    comment_type = Column(String(50), default='general')  # general, review, approval, clarification
    content = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    resolved_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    resolved_at = Column(String(255), nullable=True)
    parent_comment_id = Column(Integer, ForeignKey('form_comments.id'), nullable=True)  # For threaded comments
    attachments = Column(JSON, nullable=True)

    # Relationships
    user = relationship('User', foreign_keys=[user_id])
    resolved_by = relationship('User', foreign_keys=[resolved_by_id])


class FormValidationHistory(BaseModel):
    """Track validation issues and resolutions"""
    __tablename__ = 'form_validation_history'

    record_id = Column(Integer, ForeignKey('form_records.id', ondelete='CASCADE'), nullable=False)
    field_id = Column(Integer, ForeignKey('form_fields.id'), nullable=True)
    field_name = Column(String(200), nullable=False)
    validation_rule = Column(String(200), nullable=False)
    severity = Column(Enum(ValidationSeverityEnum), nullable=False)
    error_message = Column(Text, nullable=False)
    field_value = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(String(255), nullable=True)
    resolved_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    metadata = Column(JSON, nullable=True)


class DigitalSignature(BaseModel):
    """Digital signatures for form approvals"""
    __tablename__ = 'digital_signatures'

    record_id = Column(Integer, ForeignKey('form_records.id', ondelete='CASCADE'), nullable=False)
    signer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    signature_type = Column(String(50), nullable=False)  # doer, checker, approver
    signature_data = Column(Text, nullable=False)  # Base64 encoded signature image or hash
    signature_method = Column(String(50), default='drawn')  # drawn, typed, uploaded, certificate
    signing_timestamp = Column(String(255), nullable=False)
    ip_address = Column(String(50), nullable=True)
    device_info = Column(JSON, nullable=True)
    certificate_info = Column(JSON, nullable=True)  # For digital certificate signatures
    is_valid = Column(Boolean, default=True)
    invalidated_at = Column(String(255), nullable=True)
    invalidation_reason = Column(Text, nullable=True)

    # Relationships
    signer = relationship('User', foreign_keys=[signer_id])


class FormFieldCondition(BaseModel):
    """Conditional field visibility/requirement rules"""
    __tablename__ = 'form_field_conditions'

    field_id = Column(Integer, ForeignKey('form_fields.id', ondelete='CASCADE'), nullable=False)
    condition_type = Column(String(50), nullable=False)  # show, hide, require, disable
    trigger_field_id = Column(Integer, ForeignKey('form_fields.id'), nullable=False)
    operator = Column(String(50), nullable=False)  # equals, not_equals, contains, greater_than, less_than, etc.
    trigger_value = Column(Text, nullable=True)
    trigger_value_json = Column(JSON, nullable=True)  # For complex conditions
    logic_operator = Column(String(20), default='AND')  # AND, OR for multiple conditions
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


class BulkUpload(BaseModel):
    """Track bulk upload operations"""
    __tablename__ = 'bulk_uploads'

    template_id = Column(Integer, ForeignKey('form_templates.id'), nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # csv, xlsx
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    successful_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    status = Column(Enum(BulkUploadStatusEnum), default=BulkUploadStatusEnum.PENDING)
    started_at = Column(String(255), nullable=True)
    completed_at = Column(String(255), nullable=True)
    error_log = Column(JSON, nullable=True)  # List of errors with row numbers
    success_log = Column(JSON, nullable=True)  # List of created record IDs
    validation_errors = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    uploaded_by = relationship('User', foreign_keys=[uploaded_by_id])


class FormDraft(BaseModel):
    """Auto-save draft functionality"""
    __tablename__ = 'form_drafts'

    template_id = Column(Integer, ForeignKey('form_templates.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    record_id = Column(Integer, ForeignKey('form_records.id'), nullable=True)  # Link to existing record if editing
    draft_data = Column(JSON, nullable=False)  # Field values
    last_saved_at = Column(String(255), nullable=False)
    expires_at = Column(String(255), nullable=True)
    device_info = Column(JSON, nullable=True)

    # Relationships
    user = relationship('User', foreign_keys=[user_id])


class FormFieldValidation(BaseModel):
    """Enhanced validation rules for form fields"""
    __tablename__ = 'form_field_validations'

    field_id = Column(Integer, ForeignKey('form_fields.id', ondelete='CASCADE'), nullable=False)
    validation_type = Column(String(100), nullable=False)  # required, min, max, pattern, email, url, custom, cross_field
    validation_value = Column(Text, nullable=True)
    validation_value_json = Column(JSON, nullable=True)  # For complex validations
    error_message = Column(Text, nullable=False)
    severity = Column(Enum(ValidationSeverityEnum), default=ValidationSeverityEnum.ERROR)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    custom_validator = Column(Text, nullable=True)  # Python expression for custom validation
    depends_on_fields = Column(JSON, nullable=True)  # List of field IDs for cross-field validation


class RecordApprovalMatrix(BaseModel):
    """Define approval matrix for different templates"""
    __tablename__ = 'record_approval_matrix'

    template_id = Column(Integer, ForeignKey('form_templates.id'), nullable=False)
    approval_level = Column(Integer, nullable=False)  # 1=doer, 2=checker, 3=approver
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)  # Required role
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Specific user
    department = Column(String(100), nullable=True)  # Department-based approval
    condition = Column(JSON, nullable=True)  # Conditional approval rules
    is_required = Column(Boolean, default=True)
    is_parallel = Column(Boolean, default=False)  # Multiple approvers at same level
    timeout_hours = Column(Integer, nullable=True)  # Auto-escalation timeout
    escalation_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)


class RecordVersionHistory(BaseModel):
    """Version history for form records"""
    __tablename__ = 'record_version_history'

    record_id = Column(Integer, ForeignKey('form_records.id', ondelete='CASCADE'), nullable=False)
    version_number = Column(Integer, nullable=False)
    changed_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    change_type = Column(String(50), nullable=False)  # created, updated, status_change, approved
    change_summary = Column(Text, nullable=True)
    field_changes = Column(JSON, nullable=False)  # {"field_name": {"old": "value", "new": "value"}}
    status_before = Column(String(50), nullable=True)
    status_after = Column(String(50), nullable=True)
    snapshot_data = Column(JSON, nullable=True)  # Complete record snapshot

    # Relationships
    changed_by = relationship('User', foreign_keys=[changed_by_id])


class DataQualityRule(BaseModel):
    """Data quality rules for templates"""
    __tablename__ = 'data_quality_rules'

    template_id = Column(Integer, ForeignKey('form_templates.id'), nullable=False)
    rule_name = Column(String(200), nullable=False)
    rule_type = Column(String(100), nullable=False)  # completeness, accuracy, consistency, uniqueness, timeliness
    description = Column(Text, nullable=True)
    rule_expression = Column(Text, nullable=False)  # Python expression
    severity = Column(Enum(ValidationSeverityEnum), default=ValidationSeverityEnum.WARNING)
    is_active = Column(Boolean, default=True)
    applies_to_fields = Column(JSON, nullable=True)  # List of field names
    metadata = Column(JSON, nullable=True)


class DuplicateDetectionConfig(BaseModel):
    """Configure duplicate detection for templates"""
    __tablename__ = 'duplicate_detection_configs'

    template_id = Column(Integer, ForeignKey('form_templates.id'), nullable=False)
    field_combinations = Column(JSON, nullable=False)  # List of field name combinations to check
    detection_method = Column(String(50), default='exact')  # exact, fuzzy, phonetic
    similarity_threshold = Column(Float, nullable=True)  # For fuzzy matching (0.0-1.0)
    time_window_hours = Column(Integer, nullable=True)  # Only check duplicates within time window
    is_active = Column(Boolean, default=True)
    action = Column(String(50), default='warn')  # warn, block, flag
    custom_logic = Column(Text, nullable=True)
