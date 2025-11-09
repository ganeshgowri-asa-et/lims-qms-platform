"""
Quality and Audit Management models
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class NCStatusEnum(str, enum.Enum):
    """Non-Conformance status"""
    OPEN = "Open"
    INVESTIGATING = "Investigating"
    CAPA_IN_PROGRESS = "CAPA In Progress"
    RESOLVED = "Resolved"
    VERIFIED = "Verified"
    CLOSED = "Closed"


class AuditTypeEnum(str, enum.Enum):
    """Audit type"""
    INTERNAL = "Internal"
    EXTERNAL = "External"
    SURVEILLANCE = "Surveillance"
    CERTIFICATION = "Certification"
    CUSTOMER = "Customer"


class AuditStatusEnum(str, enum.Enum):
    """Audit status"""
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    REPORT_ISSUED = "Report Issued"


class CAPAStatusEnum(str, enum.Enum):
    """CAPA status"""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    IMPLEMENTED = "Implemented"
    VERIFIED = "Verified"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"


class RiskLevelEnum(str, enum.Enum):
    """Risk level"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class NonConformance(BaseModel):
    """Non-Conformance (NC) model"""
    __tablename__ = 'non_conformances'

    nc_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)  # Process, Product, System, Documentation
    severity = Column(Enum(RiskLevelEnum), nullable=False)
    status = Column(Enum(NCStatusEnum), default=NCStatusEnum.OPEN)

    # Where & When
    detected_date = Column(Date, nullable=False)
    detected_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    area_department = Column(String(200), nullable=True)
    process_affected = Column(String(200), nullable=True)

    # Related entities
    order_id = Column(Integer, ForeignKey('customer_orders.id'), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    equipment_id = Column(Integer, ForeignKey('equipment.id'), nullable=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=True)

    # Investigation
    root_cause = Column(Text, nullable=True)
    investigation_notes = Column(Text, nullable=True)
    immediate_action = Column(Text, nullable=True)

    # Assignment
    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    target_closure_date = Column(Date, nullable=True)
    actual_closure_date = Column(Date, nullable=True)

    # Verification
    verified_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    verified_at = Column(String(255), nullable=True)
    verification_notes = Column(Text, nullable=True)

    # Attachments
    attachments = Column(JSON, nullable=True)

    # Relationships
    capas = relationship('CAPA', back_populates='non_conformance')


class Audit(BaseModel):
    """Audit model"""
    __tablename__ = 'audits'

    audit_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    audit_type = Column(Enum(AuditTypeEnum), nullable=False)
    status = Column(Enum(AuditStatusEnum), default=AuditStatusEnum.PLANNED)

    # Planning
    planned_date = Column(Date, nullable=True)
    actual_date = Column(Date, nullable=True)
    scope = Column(Text, nullable=True)
    standard = Column(String(100), nullable=True)  # ISO 17025, ISO 9001
    areas_to_audit = Column(JSON, nullable=True)

    # Team
    lead_auditor_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    auditors = Column(JSON, nullable=True)  # List of auditor IDs
    auditee_ids = Column(JSON, nullable=True)  # List of auditee IDs

    # Execution
    opening_meeting_date = Column(Date, nullable=True)
    closing_meeting_date = Column(Date, nullable=True)
    findings = Column(JSON, nullable=True)  # List of findings with details
    observations = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)

    # Report
    report_file_path = Column(String(500), nullable=True)
    report_issued_date = Column(Date, nullable=True)
    report_issued_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Follow-up
    follow_up_date = Column(Date, nullable=True)
    follow_up_notes = Column(Text, nullable=True)


class CAPA(BaseModel):
    """Corrective and Preventive Action"""
    __tablename__ = 'capas'

    capa_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    capa_type = Column(String(50), nullable=False)  # Corrective, Preventive
    description = Column(Text, nullable=False)
    status = Column(Enum(CAPAStatusEnum), default=CAPAStatusEnum.OPEN)

    # Source
    source_type = Column(String(100), nullable=True)  # NC, Audit, Risk Assessment, Customer Complaint
    non_conformance_id = Column(Integer, ForeignKey('non_conformances.id'), nullable=True)
    audit_id = Column(Integer, ForeignKey('audits.id'), nullable=True)

    # Root cause
    root_cause = Column(Text, nullable=True)
    root_cause_analysis_method = Column(String(100), nullable=True)  # 5 Why, Fishbone, etc.

    # Action plan
    proposed_action = Column(Text, nullable=False)
    responsible_person_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    target_completion_date = Column(Date, nullable=True)
    actual_completion_date = Column(Date, nullable=True)

    # Implementation
    implementation_details = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=True)  # Attachments, photos, documents

    # Verification
    verification_method = Column(Text, nullable=True)
    verified_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    verification_date = Column(Date, nullable=True)
    verification_result = Column(Text, nullable=True)
    is_effective = Column(Boolean, nullable=True)

    # Closure
    closure_notes = Column(Text, nullable=True)
    closed_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    closed_at = Column(String(255), nullable=True)

    # Relationships
    non_conformance = relationship('NonConformance', back_populates='capas')


class RiskAssessment(BaseModel):
    """Risk Assessment model"""
    __tablename__ = 'risk_assessments'

    risk_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)  # Operational, Financial, Compliance, etc.
    area_department = Column(String(200), nullable=True)

    # Risk evaluation
    likelihood = Column(Integer, nullable=True)  # 1-5 scale
    impact = Column(Integer, nullable=True)  # 1-5 scale
    risk_score = Column(Integer, nullable=True)  # likelihood * impact
    risk_level = Column(Enum(RiskLevelEnum), nullable=True)

    # Current controls
    current_controls = Column(Text, nullable=True)

    # Risk treatment
    treatment_plan = Column(Text, nullable=True)
    responsible_person_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    target_date = Column(Date, nullable=True)

    # Residual risk (after treatment)
    residual_likelihood = Column(Integer, nullable=True)
    residual_impact = Column(Integer, nullable=True)
    residual_risk_score = Column(Integer, nullable=True)
    residual_risk_level = Column(Enum(RiskLevelEnum), nullable=True)

    # Review
    review_date = Column(Date, nullable=True)
    review_frequency_months = Column(Integer, nullable=True)
    next_review_date = Column(Date, nullable=True)
    status = Column(String(50), default='active')  # active, mitigated, closed
