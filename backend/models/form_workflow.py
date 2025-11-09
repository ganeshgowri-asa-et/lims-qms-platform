"""
Enhanced Form Workflow Models
Implements Doer-Checker-Approver workflow with state machine
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, JSON, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum
from datetime import datetime


class WorkflowStatus(str, enum.Enum):
    """Workflow status enumeration"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    CHECKER_APPROVED = "checker_approved"
    CHECKER_REJECTED = "checker_rejected"
    APPROVER_APPROVED = "approver_approved"
    APPROVER_REJECTED = "approver_rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkflowAction(str, enum.Enum):
    """Workflow actions"""
    SUBMIT = "submit"
    ASSIGN_CHECKER = "assign_checker"
    CHECKER_REVIEW = "checker_review"
    CHECKER_APPROVE = "checker_approve"
    CHECKER_REJECT = "checker_reject"
    ASSIGN_APPROVER = "assign_approver"
    APPROVER_REVIEW = "approver_review"
    APPROVER_APPROVE = "approver_approve"
    APPROVER_REJECT = "approver_reject"
    CANCEL = "cancel"
    REQUEST_CHANGES = "request_changes"
    RESUBMIT = "resubmit"


class WorkflowTransition(BaseModel):
    """Workflow state transition log"""
    __tablename__ = 'workflow_transitions'

    record_id = Column(Integer, ForeignKey('form_records.id', ondelete='CASCADE'), nullable=False)
    from_status = Column(SQLEnum(WorkflowStatus), nullable=True)
    to_status = Column(SQLEnum(WorkflowStatus), nullable=False)
    action = Column(SQLEnum(WorkflowAction), nullable=False)
    actor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    comments = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    transition_time = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    record = relationship('FormRecord', back_populates='transitions')
    actor = relationship('User', foreign_keys=[actor_id])


class FormSignature(BaseModel):
    """Digital signature for form records"""
    __tablename__ = 'form_signatures'

    record_id = Column(Integer, ForeignKey('form_records.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role = Column(String(50), nullable=False)  # doer, checker, approver
    signature_data = Column(Text, nullable=True)  # Base64 encoded signature image
    signature_hash = Column(String(256), nullable=True)  # SHA-256 hash for verification
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    signed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    certificate_data = Column(JSON, nullable=True)  # Digital certificate info
    is_verified = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    record = relationship('FormRecord', back_populates='signatures')
    user = relationship('User')


class FormValidationRule(BaseModel):
    """Advanced validation rules for form fields"""
    __tablename__ = 'form_validation_rules'

    field_id = Column(Integer, ForeignKey('form_fields.id', ondelete='CASCADE'), nullable=False)
    rule_name = Column(String(200), nullable=False)
    rule_type = Column(String(100), nullable=False)  # required, range, pattern, custom, cross_field
    rule_config = Column(JSON, nullable=False)  # Configuration parameters
    error_message = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher priority rules execute first
    depends_on_fields = Column(JSON, nullable=True)  # List of field IDs for cross-field validation

    # Relationships
    field = relationship('FormField', back_populates='validation_rules')


class FormHistory(BaseModel):
    """Version history for form records"""
    __tablename__ = 'form_history'

    record_id = Column(Integer, ForeignKey('form_records.id', ondelete='CASCADE'), nullable=False)
    version_number = Column(Integer, nullable=False)
    changed_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    change_type = Column(String(50), nullable=False)  # created, updated, status_changed, approved, rejected
    changes = Column(JSON, nullable=True)  # {"field_name": {"old": "...", "new": "..."}}
    snapshot = Column(JSON, nullable=True)  # Complete record snapshot
    comments = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    record = relationship('FormRecord', back_populates='history')
    changed_by = relationship('User')


class FormNotificationTemplate(BaseModel):
    """Notification templates for workflow stages"""
    __tablename__ = 'form_notification_templates'

    name = Column(String(200), nullable=False)
    trigger_event = Column(String(100), nullable=False)  # on_submit, on_checker_assign, etc.
    recipient_role = Column(String(50), nullable=False)  # doer, checker, approver
    subject_template = Column(String(500), nullable=False)
    body_template = Column(Text, nullable=False)  # Jinja2 template
    notification_type = Column(String(50), default='email')  # email, in_app, both
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)


class FormDataSource(BaseModel):
    """External data sources for auto-population"""
    __tablename__ = 'form_data_sources'

    name = Column(String(200), nullable=False)
    source_type = Column(String(100), nullable=False)  # api, database, file, master_data
    connection_config = Column(JSON, nullable=False)  # Connection details
    query_template = Column(Text, nullable=True)  # Query or API endpoint template
    field_mappings = Column(JSON, nullable=True)  # Map source fields to form fields
    cache_duration = Column(Integer, default=3600)  # Cache duration in seconds
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)


class FormDuplicateCheck(BaseModel):
    """Duplicate detection configuration"""
    __tablename__ = 'form_duplicate_checks'

    template_id = Column(Integer, ForeignKey('form_templates.id', ondelete='CASCADE'), nullable=False)
    check_name = Column(String(200), nullable=False)
    check_fields = Column(JSON, nullable=False)  # List of field names to check
    check_logic = Column(String(50), default='exact')  # exact, fuzzy, custom
    tolerance = Column(Integer, default=0)  # For fuzzy matching (0-100)
    is_active = Column(Boolean, default=True)
    error_message = Column(String(500), nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    template = relationship('FormTemplate', back_populates='duplicate_checks')


class FormApprovalMatrix(BaseModel):
    """Approval matrix configuration for different form types"""
    __tablename__ = 'form_approval_matrix'

    template_id = Column(Integer, ForeignKey('form_templates.id', ondelete='CASCADE'), nullable=False)
    condition = Column(JSON, nullable=True)  # Condition to apply this matrix
    requires_checker = Column(Boolean, default=True)
    requires_approver = Column(Boolean, default=True)
    auto_assign_checker = Column(Boolean, default=False)
    auto_assign_approver = Column(Boolean, default=False)
    checker_role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    approver_role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    escalation_hours = Column(Integer, nullable=True)  # Auto-escalate after N hours
    metadata = Column(JSON, nullable=True)

    # Relationships
    template = relationship('FormTemplate', back_populates='approval_matrix')
    checker_role = relationship('Role', foreign_keys=[checker_role_id])
    approver_role = relationship('Role', foreign_keys=[approver_role_id])
