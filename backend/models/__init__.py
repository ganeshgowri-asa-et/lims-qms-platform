"""
Database Models for LIMS-QMS Platform
"""
from backend.core.database import Base
from .user import User, Role, Permission
from .document import Document, DocumentVersion, DocumentLevel
from .form import FormTemplate, FormField, FormRecord, FormValue
from .data_capture import (
    FormWorkflowEvent, FormComment, FormValidationHistory, DigitalSignature,
    FormFieldCondition, BulkUpload, FormDraft, FormFieldValidation,
    RecordApprovalMatrix, RecordVersionHistory, DataQualityRule, DuplicateDetectionConfig,
    RecordStatusEnum, WorkflowActionEnum, ValidationSeverityEnum, BulkUploadStatusEnum
)
from .traceability import TraceabilityLink, AuditLog
from .workflow import Project, Task, Meeting, ActionItem
from .hr import Employee, JobPosting, Candidate, Training, Leave, Attendance, Performance
from .procurement import Vendor, RFQ, PurchaseOrder, Equipment, Calibration, Maintenance
from .financial import Expense, Invoice, Payment, Revenue
from .crm import Lead, Customer, Order, SupportTicket
from .quality import NonConformance, Audit, CAPA, RiskAssessment
from .notification import Notification

__all__ = [
    "Base",
    "User", "Role", "Permission",
    "Document", "DocumentVersion", "DocumentLevel",
    "FormTemplate", "FormField", "FormRecord", "FormValue",
    "FormWorkflowEvent", "FormComment", "FormValidationHistory", "DigitalSignature",
    "FormFieldCondition", "BulkUpload", "FormDraft", "FormFieldValidation",
    "RecordApprovalMatrix", "RecordVersionHistory", "DataQualityRule", "DuplicateDetectionConfig",
    "RecordStatusEnum", "WorkflowActionEnum", "ValidationSeverityEnum", "BulkUploadStatusEnum",
    "TraceabilityLink", "AuditLog",
    "Project", "Task", "Meeting", "ActionItem",
    "Employee", "JobPosting", "Candidate", "Training", "Leave", "Attendance", "Performance",
    "Vendor", "RFQ", "PurchaseOrder", "Equipment", "Calibration", "Maintenance",
    "Expense", "Invoice", "Payment", "Revenue",
    "Lead", "Customer", "Order", "SupportTicket",
    "NonConformance", "Audit", "CAPA", "RiskAssessment",
    "Notification"
]
