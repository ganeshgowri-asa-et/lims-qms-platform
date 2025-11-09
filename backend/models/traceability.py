"""
Traceability and Audit Trail models
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Enum, DateTime, Index, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel
import enum


class EntityTypeEnum(str, enum.Enum):
    """Entity types for traceability"""
    DOCUMENT = "document"
    FORM_RECORD = "form_record"
    PROJECT = "project"
    TASK = "task"
    EQUIPMENT = "equipment"
    CALIBRATION = "calibration"
    PURCHASE_ORDER = "purchase_order"
    CUSTOMER_ORDER = "customer_order"
    NON_CONFORMANCE = "non_conformance"
    CAPA = "capa"
    AUDIT = "audit"
    VENDOR = "vendor"
    EMPLOYEE = "employee"
    TRAINING = "training"
    SAMPLE = "sample"
    TEST_RESULT = "test_result"
    REQUIREMENT = "requirement"
    DATA_POINT = "data_point"


class ActionTypeEnum(str, enum.Enum):
    """Action types for audit log"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    SUBMIT = "submit"
    APPROVE = "approve"
    REJECT = "reject"
    REVIEW = "review"
    DOWNLOAD = "download"
    PRINT = "print"
    EXPORT = "export"
    TRANSFER = "transfer"
    RECEIVE = "receive"
    SIGN = "sign"
    VERIFY = "verify"


class DataLineageStageEnum(str, enum.Enum):
    """Data lineage stages (Medallion Architecture)"""
    BRONZE = "bronze"  # Raw data
    SILVER = "silver"  # Processed/cleaned data
    GOLD = "gold"      # Final/aggregated data


class CustodyEventTypeEnum(str, enum.Enum):
    """Chain of custody event types"""
    RECEIVED = "received"
    TRANSFERRED = "transferred"
    STORED = "stored"
    TESTED = "tested"
    DISPOSED = "disposed"
    RETURNED = "returned"


class RequirementStatusEnum(str, enum.Enum):
    """Requirement traceability status"""
    DRAFT = "draft"
    ACTIVE = "active"
    VERIFIED = "verified"
    OBSOLETE = "obsolete"


class TraceabilityLink(BaseModel):
    """Links between entities for traceability"""
    __tablename__ = 'traceability_links'

    source_entity_type = Column(Enum(EntityTypeEnum), nullable=False)
    source_entity_id = Column(Integer, nullable=False)
    target_entity_type = Column(Enum(EntityTypeEnum), nullable=False)
    target_entity_id = Column(Integer, nullable=False)
    link_type = Column(String(100), nullable=False)  # "parent", "child", "related", "derived_from"
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Composite index for efficient lookups
    # __table_args__ = (
    #     Index('idx_source', 'source_entity_type', 'source_entity_id'),
    #     Index('idx_target', 'target_entity_type', 'target_entity_id'),
    # )


class AuditLog(BaseModel):
    """Comprehensive audit trail for all actions (immutable, event-sourced)"""
    __tablename__ = 'audit_logs'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    entity_type = Column(Enum(EntityTypeEnum), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(Enum(ActionTypeEnum), nullable=False)
    description = Column(Text, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    session_id = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)  # Physical location or device
    reason = Column(Text, nullable=True)  # Mandatory reason for change
    metadata = Column(JSON, nullable=True)

    # Immutability & blockchain-inspired fields
    event_sequence = Column(Integer, nullable=False)  # Sequential event number
    checksum = Column(String(64), nullable=True)  # SHA-256 of event data
    previous_checksum = Column(String(64), nullable=True)  # Link to previous event

    # Relationship
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_user_time', 'user_id', 'created_at'),
        Index('idx_audit_action', 'action', 'created_at'),
    )


class DataLineage(BaseModel):
    """Track data transformations through pipeline stages (Medallion Architecture)"""
    __tablename__ = 'data_lineage'

    # Source data
    source_entity_type = Column(Enum(EntityTypeEnum), nullable=False)
    source_entity_id = Column(Integer, nullable=False)
    source_stage = Column(Enum(DataLineageStageEnum), nullable=False)

    # Target data
    target_entity_type = Column(Enum(EntityTypeEnum), nullable=False)
    target_entity_id = Column(Integer, nullable=False)
    target_stage = Column(Enum(DataLineageStageEnum), nullable=False)

    # Transformation details
    transformation_type = Column(String(100), nullable=False)  # "calculation", "aggregation", "cleaning", etc.
    transformation_logic = Column(Text, nullable=True)  # SQL query, formula, algorithm description
    equipment_id = Column(Integer, ForeignKey('equipment.id'), nullable=True)  # Test equipment used
    software_version = Column(String(100), nullable=True)
    performed_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    performed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Data quality
    data_quality_score = Column(Float, nullable=True)  # 0-100
    validation_status = Column(String(50), nullable=True)  # "passed", "failed", "warning"
    metadata = Column(JSON, nullable=True)

    # Relationships
    equipment = relationship("Equipment", foreign_keys=[equipment_id])
    performed_by = relationship("User", foreign_keys=[performed_by_id])

    __table_args__ = (
        Index('idx_lineage_source', 'source_entity_type', 'source_entity_id'),
        Index('idx_lineage_target', 'target_entity_type', 'target_entity_id'),
        Index('idx_lineage_stage', 'source_stage', 'target_stage'),
    )


class RequirementTraceability(BaseModel):
    """Requirements Traceability Matrix (RTM) - Link requirements to evidence"""
    __tablename__ = 'requirement_traceability'

    # Requirement identification
    requirement_number = Column(String(100), nullable=False, unique=True, index=True)
    requirement_title = Column(String(500), nullable=False)
    requirement_description = Column(Text, nullable=True)
    requirement_source = Column(String(200), nullable=True)  # "ISO 17025:2017 5.6.2.1.1", "Customer Spec", etc.
    requirement_category = Column(String(100), nullable=True)  # "Equipment", "Personnel", "Method", etc.
    requirement_priority = Column(String(50), nullable=True)  # "critical", "high", "medium", "low"
    status = Column(Enum(RequirementStatusEnum), default=RequirementStatusEnum.DRAFT, nullable=False)

    # Links to evidence
    linked_entity_type = Column(Enum(EntityTypeEnum), nullable=True)
    linked_entity_id = Column(Integer, nullable=True)

    # Test coverage
    test_case_reference = Column(String(200), nullable=True)
    test_result_reference = Column(String(200), nullable=True)
    verification_method = Column(String(200), nullable=True)  # "inspection", "test", "analysis", "demonstration"
    verification_status = Column(String(50), nullable=True)  # "verified", "partially_verified", "not_verified"
    verification_date = Column(DateTime(timezone=True), nullable=True)
    verified_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Compliance mapping
    compliance_standards = Column(JSON, nullable=True)  # ["ISO 17025", "ISO 9001", "GLP"]
    metadata = Column(JSON, nullable=True)

    # Relationship
    verified_by = relationship("User", foreign_keys=[verified_by_id])

    __table_args__ = (
        Index('idx_requirement_status', 'status', 'requirement_category'),
        Index('idx_requirement_linked', 'linked_entity_type', 'linked_entity_id'),
    )


class ChainOfCustody(BaseModel):
    """Track chain of custody for samples, equipment, and materials"""
    __tablename__ = 'chain_of_custody'

    # Entity being tracked
    entity_type = Column(Enum(EntityTypeEnum), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    entity_identifier = Column(String(200), nullable=False)  # Sample ID, Equipment ID, etc.

    # Custody event
    event_type = Column(Enum(CustodyEventTypeEnum), nullable=False)
    event_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Parties involved
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    from_location = Column(String(200), nullable=True)
    to_location = Column(String(200), nullable=True)

    # Signatures (digital)
    from_signature = Column(String(500), nullable=True)  # Digital signature or confirmation
    to_signature = Column(String(500), nullable=True)
    witness_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    witness_signature = Column(String(500), nullable=True)

    # Condition tracking
    condition_before = Column(String(200), nullable=True)  # "good", "sealed", "refrigerated", etc.
    condition_after = Column(String(200), nullable=True)
    temperature_log = Column(JSON, nullable=True)  # Temperature monitoring data
    integrity_check = Column(Boolean, default=True)
    seal_number = Column(String(100), nullable=True)

    # Transport details
    transport_method = Column(String(200), nullable=True)
    tracking_number = Column(String(200), nullable=True)
    estimated_arrival = Column(DateTime(timezone=True), nullable=True)

    # Notes and metadata
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])
    witness = relationship("User", foreign_keys=[witness_id])

    __table_args__ = (
        Index('idx_custody_entity', 'entity_type', 'entity_id'),
        Index('idx_custody_event', 'event_type', 'event_timestamp'),
        Index('idx_custody_users', 'from_user_id', 'to_user_id'),
    )


class EntitySnapshot(BaseModel):
    """Store complete snapshots of entity state for version comparison"""
    __tablename__ = 'entity_snapshots'

    entity_type = Column(Enum(EntityTypeEnum), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    snapshot_data = Column(JSON, nullable=False)  # Complete entity state as JSON
    snapshot_hash = Column(String(64), nullable=False)  # SHA-256 hash for integrity
    snapshot_size = Column(Integer, nullable=True)  # Size in bytes
    diff_from_previous = Column(JSON, nullable=True)  # Diff from previous version
    snapshot_trigger = Column(String(100), nullable=True)  # "manual", "approval", "scheduled", "pre_delete"
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationship
    created_by = relationship("User", foreign_keys=[created_by_id])

    __table_args__ = (
        Index('idx_snapshot_entity', 'entity_type', 'entity_id', 'version_number'),
        Index('idx_snapshot_created', 'created_at'),
    )


class ComplianceEvidence(BaseModel):
    """Store compliance evidence and audit-ready reports"""
    __tablename__ = 'compliance_evidence'

    # Compliance identification
    evidence_number = Column(String(100), nullable=False, unique=True, index=True)
    evidence_type = Column(String(100), nullable=False)  # "calibration", "training", "audit", "test_result", etc.
    compliance_standards = Column(JSON, nullable=False)  # ["ISO 17025", "ISO 9001"]
    requirement_reference = Column(String(200), nullable=True)  # Link to specific requirement

    # Linked entities
    entity_type = Column(Enum(EntityTypeEnum), nullable=True)
    entity_id = Column(Integer, nullable=True)

    # Evidence details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    evidence_date = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False, default="valid")  # "valid", "expired", "superseded"

    # Supporting documentation
    document_references = Column(JSON, nullable=True)  # List of document IDs
    attachment_urls = Column(JSON, nullable=True)
    digital_signature = Column(String(500), nullable=True)

    # Audit trail
    reviewed_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_comments = Column(Text, nullable=True)

    # Metadata
    metadata = Column(JSON, nullable=True)

    # Relationship
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])

    __table_args__ = (
        Index('idx_evidence_type', 'evidence_type', 'status'),
        Index('idx_evidence_entity', 'entity_type', 'entity_id'),
        Index('idx_evidence_dates', 'evidence_date', 'expiry_date'),
    )


class ImpactAnalysis(BaseModel):
    """Track impact analysis for document changes"""
    __tablename__ = 'impact_analysis'

    # Source change
    source_entity_type = Column(Enum(EntityTypeEnum), nullable=False)
    source_entity_id = Column(Integer, nullable=False)
    change_description = Column(Text, nullable=False)
    change_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Impact assessment
    impact_scope = Column(String(50), nullable=False)  # "low", "medium", "high", "critical"
    affected_entities = Column(JSON, nullable=False)  # List of {entity_type, entity_id, impact_description}
    estimated_effort_hours = Column(Float, nullable=True)
    risk_level = Column(String(50), nullable=True)  # "low", "medium", "high"

    # Mitigation plan
    mitigation_plan = Column(Text, nullable=True)
    action_items = Column(JSON, nullable=True)  # List of action item IDs
    stakeholders_notified = Column(JSON, nullable=True)  # List of user IDs

    # Status tracking
    analysis_status = Column(String(50), nullable=False, default="draft")  # "draft", "under_review", "approved", "implemented"
    analyzed_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    approved_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    metadata = Column(JSON, nullable=True)

    # Relationships
    analyzed_by = relationship("User", foreign_keys=[analyzed_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])

    __table_args__ = (
        Index('idx_impact_source', 'source_entity_type', 'source_entity_id'),
        Index('idx_impact_status', 'analysis_status', 'impact_scope'),
    )
