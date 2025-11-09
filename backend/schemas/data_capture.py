"""
Pydantic Schemas for Data Capture API
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime


# Form Record Schemas
class RecordCreate(BaseModel):
    """Schema for creating a new record"""
    template_id: int
    title: Optional[str] = None
    values: Dict[str, Any]
    metadata: Optional[Dict] = None
    auto_submit: bool = False


class RecordUpdate(BaseModel):
    """Schema for updating a record"""
    title: Optional[str] = None
    values: Dict[str, Any]
    metadata: Optional[Dict] = None


class RecordResponse(BaseModel):
    """Schema for record response"""
    id: int
    record_number: str
    title: Optional[str]
    status: str
    template: Optional[Dict]
    doer: Optional[Dict]
    checker: Optional[Dict]
    approver: Optional[Dict]
    submitted_at: Optional[str]
    checked_at: Optional[str]
    approved_at: Optional[str]
    rejected_at: Optional[str]
    rejection_reason: Optional[str]
    checker_comments: Optional[str]
    approver_comments: Optional[str]
    revision_number: int
    completion_percentage: int
    validation_score: int
    metadata: Optional[Dict]
    attachments: Optional[List]
    tags: Optional[List]
    due_date: Optional[str]
    last_modified_at: Optional[str]
    created_at: str
    created_by: Optional[Dict]
    values: Optional[Dict] = None

    class Config:
        from_attributes = True


# Workflow Schemas
class WorkflowAction(BaseModel):
    """Schema for workflow actions"""
    action: str = Field(..., description="Action: approve, reject, request_revision")
    comments: Optional[str] = None
    metadata: Optional[Dict] = None


class CommentCreate(BaseModel):
    """Schema for creating a comment"""
    content: str
    field_id: Optional[int] = None
    comment_type: str = "general"
    parent_comment_id: Optional[int] = None


class CommentResponse(BaseModel):
    """Schema for comment response"""
    id: int
    content: str
    comment_type: str
    field_id: Optional[int]
    user: Optional[Dict]
    created_at: str
    is_resolved: bool
    parent_comment_id: Optional[int]

    class Config:
        from_attributes = True


# Validation Schemas
class ValidationRequest(BaseModel):
    """Schema for validation request"""
    template_id: int
    values: Dict[str, Any]


class ValidationError(BaseModel):
    """Schema for validation error"""
    field: str
    message: str
    severity: str
    rule: str


class ValidationResponse(BaseModel):
    """Schema for validation response"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    completion_percentage: int
    validation_score: int
    duplicates: List[Dict] = []


# Draft Schemas
class DraftSave(BaseModel):
    """Schema for saving draft"""
    template_id: int
    values: Dict[str, Any]
    record_id: Optional[int] = None


class DraftResponse(BaseModel):
    """Schema for draft response"""
    id: int
    draft_data: Dict[str, Any]
    last_saved_at: str

    class Config:
        from_attributes = True


# Signature Schemas
class SignatureCreate(BaseModel):
    """Schema for creating signature"""
    signature_type: str = Field(..., description="Type: doer, checker, approver")
    signature_data: str = Field(..., description="Base64 encoded signature")
    signature_method: str = Field(default="drawn", description="Method: drawn, typed, uploaded, certificate")
    ip_address: Optional[str] = None
    device_info: Optional[Dict] = None
    certificate_info: Optional[Dict] = None


class SignatureResponse(BaseModel):
    """Schema for signature response"""
    id: int
    signature_type: str
    signer: Optional[Dict]
    signature_method: str
    signing_timestamp: str
    is_valid: bool
    invalidated_at: Optional[str]
    invalidation_reason: Optional[str]

    class Config:
        from_attributes = True


# Bulk Upload Schemas
class BulkUploadResponse(BaseModel):
    """Schema for bulk upload response"""
    id: int
    file_name: str
    status: str
    total_rows: int
    processed_rows: int
    successful_rows: int
    failed_rows: int
    started_at: Optional[str]
    completed_at: Optional[str]
    error_log: Optional[List]
    success_log: Optional[List]
    validation_errors: Optional[List]

    class Config:
        from_attributes = True


# Field Validation Rule Schemas
class ValidationRuleCreate(BaseModel):
    """Schema for creating validation rule"""
    field_id: int
    validation_type: str
    validation_value: Optional[str] = None
    validation_value_json: Optional[Dict] = None
    error_message: str
    severity: str = "error"
    order: int = 0
    custom_validator: Optional[str] = None
    depends_on_fields: Optional[List[int]] = None


class ValidationRuleResponse(BaseModel):
    """Schema for validation rule response"""
    id: int
    field_id: int
    validation_type: str
    validation_value: Optional[str]
    validation_value_json: Optional[Dict]
    error_message: str
    severity: str
    order: int
    is_active: bool
    custom_validator: Optional[str]
    depends_on_fields: Optional[List[int]]

    class Config:
        from_attributes = True


# Conditional Field Schemas
class FieldConditionCreate(BaseModel):
    """Schema for creating field condition"""
    field_id: int
    condition_type: str = Field(..., description="Type: show, hide, require, disable")
    trigger_field_id: int
    operator: str = Field(..., description="Operator: equals, not_equals, contains, greater_than, less_than")
    trigger_value: Optional[str] = None
    trigger_value_json: Optional[Dict] = None
    logic_operator: str = "AND"
    order: int = 0


class FieldConditionResponse(BaseModel):
    """Schema for field condition response"""
    id: int
    field_id: int
    condition_type: str
    trigger_field_id: int
    operator: str
    trigger_value: Optional[str]
    trigger_value_json: Optional[Dict]
    logic_operator: str
    order: int
    is_active: bool

    class Config:
        from_attributes = True


# Approval Matrix Schemas
class ApprovalMatrixCreate(BaseModel):
    """Schema for creating approval matrix"""
    template_id: int
    approval_level: int = Field(..., description="Level: 1=doer, 2=checker, 3=approver")
    role_id: Optional[int] = None
    user_id: Optional[int] = None
    department: Optional[str] = None
    condition: Optional[Dict] = None
    is_required: bool = True
    is_parallel: bool = False
    timeout_hours: Optional[int] = None
    escalation_user_id: Optional[int] = None


class ApprovalMatrixResponse(BaseModel):
    """Schema for approval matrix response"""
    id: int
    template_id: int
    approval_level: int
    role_id: Optional[int]
    user_id: Optional[int]
    department: Optional[str]
    condition: Optional[Dict]
    is_required: bool
    is_parallel: bool
    timeout_hours: Optional[int]
    escalation_user_id: Optional[int]

    class Config:
        from_attributes = True


# Data Quality Rule Schemas
class DataQualityRuleCreate(BaseModel):
    """Schema for creating data quality rule"""
    template_id: int
    rule_name: str
    rule_type: str = Field(..., description="Type: completeness, accuracy, consistency, uniqueness, timeliness")
    description: Optional[str] = None
    rule_expression: str
    severity: str = "warning"
    applies_to_fields: Optional[List[str]] = None
    metadata: Optional[Dict] = None


class DataQualityRuleResponse(BaseModel):
    """Schema for data quality rule response"""
    id: int
    template_id: int
    rule_name: str
    rule_type: str
    description: Optional[str]
    rule_expression: str
    severity: str
    is_active: bool
    applies_to_fields: Optional[List[str]]
    metadata: Optional[Dict]

    class Config:
        from_attributes = True


# Duplicate Detection Config Schemas
class DuplicateDetectionCreate(BaseModel):
    """Schema for creating duplicate detection config"""
    template_id: int
    field_combinations: List[List[str]] = Field(..., description="List of field combinations to check")
    detection_method: str = "exact"
    similarity_threshold: Optional[float] = None
    time_window_hours: Optional[int] = None
    action: str = "warn"
    custom_logic: Optional[str] = None


class DuplicateDetectionResponse(BaseModel):
    """Schema for duplicate detection config response"""
    id: int
    template_id: int
    field_combinations: List[List[str]]
    detection_method: str
    similarity_threshold: Optional[float]
    time_window_hours: Optional[int]
    is_active: bool
    action: str
    custom_logic: Optional[str]

    class Config:
        from_attributes = True


# Notification Schemas
class NotificationResponse(BaseModel):
    """Schema for notification response"""
    id: int
    title: str
    message: str
    notification_type: str
    category: str
    is_read: bool
    read_at: Optional[str]
    link: Optional[str]
    metadata: Optional[Dict]
    priority: str
    created_at: str

    class Config:
        from_attributes = True


# List Response Schemas
class RecordListResponse(BaseModel):
    """Schema for paginated record list"""
    total: int
    records: List[RecordResponse]
    skip: int
    limit: int


class WorkflowHistoryResponse(BaseModel):
    """Schema for workflow history"""
    id: int
    action: str
    from_status: Optional[str]
    to_status: str
    actor: Optional[Dict]
    comments: Optional[str]
    timestamp: str
    metadata: Optional[Dict]


class TraceabilityLinkResponse(BaseModel):
    """Schema for traceability link"""
    id: int
    source_type: str
    source_id: int
    target_type: str
    target_id: int
    link_type: str
    description: Optional[str]
    created_at: str

    class Config:
        from_attributes = True
