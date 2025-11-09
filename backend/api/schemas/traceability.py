"""
Pydantic schemas for Traceability and Audit Trail API
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# Enums matching the database models
class EntityTypeEnum(str, Enum):
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


class ActionTypeEnum(str, Enum):
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


class DataLineageStageEnum(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class CustodyEventTypeEnum(str, Enum):
    RECEIVED = "received"
    TRANSFERRED = "transferred"
    STORED = "stored"
    TESTED = "tested"
    DISPOSED = "disposed"
    RETURNED = "returned"


class RequirementStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    VERIFIED = "verified"
    OBSOLETE = "obsolete"


# ==================== TRACEABILITY LINK SCHEMAS ====================

class TraceabilityLinkCreate(BaseModel):
    source_entity_type: EntityTypeEnum
    source_entity_id: int
    target_entity_type: EntityTypeEnum
    target_entity_id: int
    link_type: str = Field(..., description="Type of link: parent, child, related, derived_from, etc.")
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TraceabilityLinkResponse(BaseModel):
    id: int
    source_entity_type: str
    source_entity_id: int
    target_entity_type: str
    target_entity_id: int
    link_type: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    created_by_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class TraceabilityTreeNode(BaseModel):
    entity_type: str
    entity_id: int
    entity_details: Optional[Dict[str, Any]] = None
    depth: int
    link_type: Optional[str] = None
    link_description: Optional[str] = None
    downstream: Optional[List['TraceabilityTreeNode']] = None
    upstream: Optional[List['TraceabilityTreeNode']] = None
    total_dependencies: int = 0
    circular_reference: bool = False
    max_depth_reached: bool = False


class BidirectionalLinksResponse(BaseModel):
    entity: Dict[str, Any]
    downstream: List[TraceabilityTreeNode]
    upstream: List[TraceabilityTreeNode]


# ==================== AUDIT LOG SCHEMAS ====================

class AuditLogResponse(BaseModel):
    id: int
    event_sequence: int
    user_id: Optional[int] = None
    entity_type: str
    entity_id: int
    action: str
    description: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[str] = None
    reason: Optional[str] = None
    checksum: Optional[str] = None
    previous_checksum: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogSearchRequest(BaseModel):
    user_id: Optional[int] = None
    entity_type: Optional[EntityTypeEnum] = None
    entity_id: Optional[int] = None
    action: Optional[ActionTypeEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    ip_address: Optional[str] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)


class AuditLogSearchResponse(BaseModel):
    total: int
    limit: int
    offset: int
    results: List[Dict[str, Any]]


class AuditChainIntegrityResponse(BaseModel):
    total_events_checked: int
    integrity_intact: bool
    issues_found: int
    issues: List[Dict[str, Any]]


# ==================== DATA LINEAGE SCHEMAS ====================

class DataLineageCreate(BaseModel):
    source_entity_type: EntityTypeEnum
    source_entity_id: int
    source_stage: DataLineageStageEnum
    target_entity_type: EntityTypeEnum
    target_entity_id: int
    target_stage: DataLineageStageEnum
    transformation_type: str = Field(..., description="calculation, aggregation, cleaning, etc.")
    transformation_logic: Optional[str] = Field(None, description="SQL query, formula, algorithm")
    equipment_id: Optional[int] = None
    software_version: Optional[str] = None
    data_quality_score: Optional[float] = Field(None, ge=0, le=100)
    validation_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DataLineageResponse(BaseModel):
    id: int
    source_entity_type: str
    source_entity_id: int
    source_stage: str
    target_entity_type: str
    target_entity_id: int
    target_stage: str
    transformation_type: str
    transformation_logic: Optional[str] = None
    equipment_id: Optional[int] = None
    software_version: Optional[str] = None
    performed_by_id: Optional[int] = None
    performed_at: datetime
    data_quality_score: Optional[float] = None
    validation_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DataLineagePathResponse(BaseModel):
    lineage_path: List[Dict[str, Any]]
    total_stages: int


# ==================== REQUIREMENTS TRACEABILITY MATRIX ====================

class RequirementCreate(BaseModel):
    requirement_number: str
    requirement_title: str
    requirement_description: Optional[str] = None
    requirement_source: Optional[str] = Field(None, description="ISO 17025:2017 5.6.2.1.1, Customer Spec, etc.")
    requirement_category: Optional[str] = Field(None, description="Equipment, Personnel, Method, etc.")
    requirement_priority: Optional[str] = Field(None, description="critical, high, medium, low")
    compliance_standards: Optional[List[str]] = None


class RequirementUpdate(BaseModel):
    requirement_title: Optional[str] = None
    requirement_description: Optional[str] = None
    requirement_source: Optional[str] = None
    requirement_category: Optional[str] = None
    requirement_priority: Optional[str] = None
    status: Optional[RequirementStatusEnum] = None
    verification_method: Optional[str] = None
    verification_status: Optional[str] = None
    compliance_standards: Optional[List[str]] = None


class RequirementLinkRequest(BaseModel):
    requirement_id: int
    entity_type: EntityTypeEnum
    entity_id: int
    verification_method: Optional[str] = Field(None, description="inspection, test, analysis, demonstration")


class RequirementResponse(BaseModel):
    id: int
    requirement_number: str
    requirement_title: str
    requirement_description: Optional[str] = None
    requirement_source: Optional[str] = None
    requirement_category: Optional[str] = None
    requirement_priority: Optional[str] = None
    status: str
    linked_entity_type: Optional[str] = None
    linked_entity_id: Optional[int] = None
    verification_method: Optional[str] = None
    verification_status: Optional[str] = None
    verification_date: Optional[datetime] = None
    verified_by_id: Optional[int] = None
    compliance_standards: Optional[List[str]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RTMCoverageReport(BaseModel):
    summary: Dict[str, Any]
    by_category: Dict[str, List[Dict[str, Any]]]
    gaps: List[Dict[str, Any]]


# ==================== CHAIN OF CUSTODY SCHEMAS ====================

class ChainOfCustodyCreate(BaseModel):
    entity_type: EntityTypeEnum
    entity_id: int
    entity_identifier: str = Field(..., description="Sample ID, Equipment ID, etc.")
    event_type: CustodyEventTypeEnum
    from_user_id: Optional[int] = None
    to_user_id: Optional[int] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    condition_before: Optional[str] = None
    condition_after: Optional[str] = None
    from_signature: Optional[str] = None
    to_signature: Optional[str] = None
    witness_id: Optional[int] = None
    seal_number: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChainOfCustodyResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    entity_identifier: str
    event_type: str
    event_timestamp: datetime
    from_user_id: Optional[int] = None
    to_user_id: Optional[int] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    condition_before: Optional[str] = None
    condition_after: Optional[str] = None
    integrity_check: bool
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== VERSION COMPARISON SCHEMAS ====================

class SnapshotCreate(BaseModel):
    entity_type: EntityTypeEnum
    entity_id: int
    snapshot_data: Dict[str, Any]
    snapshot_trigger: str = Field(default="manual", description="manual, approval, scheduled, pre_delete")
    notes: Optional[str] = None


class SnapshotResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    version_number: int
    snapshot_hash: str
    snapshot_size: Optional[int] = None
    snapshot_trigger: Optional[str] = None
    created_at: datetime
    created_by_id: Optional[int] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VersionComparisonRequest(BaseModel):
    entity_type: EntityTypeEnum
    entity_id: int
    version1: int
    version2: int


class VersionComparisonResponse(BaseModel):
    version1: Dict[str, Any]
    version2: Dict[str, Any]
    diff: Dict[str, Any]


# ==================== COMPLIANCE EVIDENCE SCHEMAS ====================

class ComplianceEvidenceCreate(BaseModel):
    evidence_number: str
    evidence_type: str = Field(..., description="calibration, training, audit, test_result, etc.")
    title: str
    description: Optional[str] = None
    compliance_standards: List[str] = Field(..., description="['ISO 17025', 'ISO 9001']")
    evidence_date: datetime
    expiry_date: Optional[datetime] = None
    entity_type: Optional[EntityTypeEnum] = None
    entity_id: Optional[int] = None
    requirement_reference: Optional[str] = None
    document_references: Optional[List[int]] = None


class ComplianceEvidenceResponse(BaseModel):
    id: int
    evidence_number: str
    evidence_type: str
    title: str
    description: Optional[str] = None
    compliance_standards: List[str]
    evidence_date: datetime
    expiry_date: Optional[datetime] = None
    status: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    requirement_reference: Optional[str] = None
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComplianceReportRequest(BaseModel):
    standards: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ComplianceReportResponse(BaseModel):
    report_generated: str
    filters: Dict[str, Any]
    summary: Dict[str, Any]
    by_type: Dict[str, List[Dict[str, Any]]]
    by_standard: Dict[str, List[str]]


# ==================== IMPACT ANALYSIS SCHEMAS ====================

class ImpactAnalysisRequest(BaseModel):
    entity_type: EntityTypeEnum
    entity_id: int
    change_description: str


class ImpactAnalysisResponse(BaseModel):
    source_entity: Dict[str, Any]
    change_description: str
    impact_scope: str
    total_affected: int
    affected_entities: List[Dict[str, Any]]
    impact_tree: TraceabilityTreeNode


# ==================== GENERAL SCHEMAS ====================

class EntityReference(BaseModel):
    entity_type: EntityTypeEnum
    entity_id: int


class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
