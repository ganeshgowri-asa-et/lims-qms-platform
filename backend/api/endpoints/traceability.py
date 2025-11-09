"""
Traceability and Audit Trail API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.core.database import get_db
from backend.api.dependencies import get_current_user
from backend.models.user import User
from backend.services.traceability_service import TraceabilityService
from backend.services.audit_service import AuditService
from backend.services.audit_listeners import set_audit_context, clear_audit_context
from backend.api.schemas.traceability import (
    TraceabilityLinkCreate,
    TraceabilityLinkResponse,
    TraceabilityTreeNode,
    BidirectionalLinksResponse,
    AuditLogResponse,
    AuditLogSearchRequest,
    AuditLogSearchResponse,
    AuditChainIntegrityResponse,
    DataLineageCreate,
    DataLineageResponse,
    DataLineagePathResponse,
    RequirementCreate,
    RequirementUpdate,
    RequirementLinkRequest,
    RequirementResponse,
    RTMCoverageReport,
    ChainOfCustodyCreate,
    ChainOfCustodyResponse,
    SnapshotCreate,
    SnapshotResponse,
    VersionComparisonRequest,
    VersionComparisonResponse,
    ComplianceEvidenceCreate,
    ComplianceEvidenceResponse,
    ComplianceReportRequest,
    ComplianceReportResponse,
    ImpactAnalysisRequest,
    ImpactAnalysisResponse,
    EntityTypeEnum,
    ActionTypeEnum,
    SuccessResponse
)

router = APIRouter()


def setup_audit_context(request: Request, current_user: User, db: Session):
    """Helper to set up audit context from request"""
    set_audit_context(
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session_id=request.headers.get("x-session-id")
    )


# ==================== DOCUMENT LINEAGE & TRACEABILITY ====================

@router.post("/links", response_model=TraceabilityLinkResponse, tags=["Traceability Links"])
async def create_traceability_link(
    link: TraceabilityLinkCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new traceability link between entities

    Links can be:
    - parent/child (document hierarchy)
    - derived_from (data lineage)
    - related (cross-references)
    - implements (requirement to implementation)
    """
    setup_audit_context(request, current_user, db)

    try:
        service = TraceabilityService(db)
        result = service.create_traceability_link(
            source_entity_type=link.source_entity_type,
            source_entity_id=link.source_entity_id,
            target_entity_type=link.target_entity_type,
            target_entity_id=link.target_entity_id,
            link_type=link.link_type,
            description=link.description,
            metadata=link.metadata,
            created_by_id=current_user.id
        )
        return result
    finally:
        clear_audit_context()


@router.get("/forward/{entity_type}/{entity_id}", response_model=TraceabilityTreeNode, tags=["Traceability Links"])
async def get_forward_traceability(
    entity_type: EntityTypeEnum,
    entity_id: int,
    max_depth: int = Query(default=10, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get forward traceability (Level 1 → 2 → 3 → 4 → 5)

    Shows all downstream dependencies:
    - Policy → Procedures → Work Instructions → Forms → Records
    """
    service = TraceabilityService(db)
    result = service.get_forward_traceability(
        entity_type=entity_type,
        entity_id=entity_id,
        max_depth=max_depth
    )
    return result


@router.get("/backward/{entity_type}/{entity_id}", response_model=TraceabilityTreeNode, tags=["Traceability Links"])
async def get_backward_traceability(
    entity_type: EntityTypeEnum,
    entity_id: int,
    max_depth: int = Query(default=10, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get backward traceability (Level 5 → 4 → 3 → 2 → 1)

    Shows all upstream sources:
    - Records → Forms → Work Instructions → Procedures → Policy
    """
    service = TraceabilityService(db)
    result = service.get_backward_traceability(
        entity_type=entity_type,
        entity_id=entity_id,
        max_depth=max_depth
    )
    return result


@router.get("/bidirectional/{entity_type}/{entity_id}", response_model=BidirectionalLinksResponse, tags=["Traceability Links"])
async def get_bidirectional_links(
    entity_type: EntityTypeEnum,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get bidirectional links for easy navigation

    Returns both upstream and downstream links (1 level deep)
    """
    service = TraceabilityService(db)
    result = service.get_bidirectional_links(
        entity_type=entity_type,
        entity_id=entity_id
    )
    return result


@router.post("/impact-analysis", response_model=ImpactAnalysisResponse, tags=["Traceability Links"])
async def analyze_impact(
    request_data: ImpactAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze impact of changing an entity

    Returns:
    - All affected downstream entities
    - Impact scope (low/medium/high/critical)
    - Complete impact tree
    """
    service = TraceabilityService(db)
    result = service.get_impact_analysis(
        entity_type=request_data.entity_type,
        entity_id=request_data.entity_id,
        change_description=request_data.change_description
    )
    return result


# ==================== AUDIT TRAIL ====================

@router.get("/audit-logs/{entity_type}/{entity_id}", response_model=List[dict], tags=["Audit Trail"])
async def get_entity_audit_history(
    entity_type: EntityTypeEnum,
    entity_id: int,
    limit: Optional[int] = Query(default=None, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete audit history for an entity

    Returns immutable, blockchain-inspired audit trail with:
    - Who: User ID and details
    - What: Action and changes (old vs new values)
    - When: Timestamp (UTC)
    - Where: IP address, location
    - Why: Reason for change
    """
    service = AuditService(db)
    result = service.get_entity_audit_history(
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit
    )
    return result


@router.post("/audit-logs/search", response_model=AuditLogSearchResponse, tags=["Audit Trail"])
async def search_audit_logs(
    search: AuditLogSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search audit logs with filters

    Supports:
    - Filter by user, entity type, action type
    - Date range filtering
    - IP address filtering
    - Pagination
    """
    service = AuditService(db)
    result = service.search_audit_logs(
        user_id=search.user_id,
        entity_type=search.entity_type,
        entity_id=search.entity_id,
        action=search.action,
        start_date=search.start_date,
        end_date=search.end_date,
        ip_address=search.ip_address,
        limit=search.limit,
        offset=search.offset
    )
    return result


@router.get("/audit-logs/verify-integrity", response_model=AuditChainIntegrityResponse, tags=["Audit Trail"])
async def verify_audit_chain_integrity(
    start_sequence: Optional[int] = None,
    end_sequence: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify blockchain-inspired audit chain integrity

    Checks:
    - Checksum chain continuity
    - Event data integrity (tampering detection)
    - Sequential event ordering
    """
    service = AuditService(db)
    result = service.verify_audit_chain_integrity(
        start_sequence=start_sequence,
        end_sequence=end_sequence
    )
    return result


@router.post("/audit-logs/export", response_model=dict, tags=["Audit Trail"])
async def export_audit_logs(
    entity_type: Optional[EntityTypeEnum] = None,
    entity_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    format: str = Query(default="json", regex="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export audit logs for compliance audits

    Supports JSON and CSV formats
    Perfect for ISO 17025/9001 audits
    """
    service = AuditService(db)
    result = service.export_audit_log(
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        format=format
    )
    return result


@router.get("/audit-logs/user-activity/{user_id}", response_model=dict, tags=["Audit Trail"])
async def get_user_activity_summary(
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summary of user activity for audit purposes"""
    service = AuditService(db)
    result = service.get_user_activity_summary(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    return result


@router.get("/audit-logs/reconstruct/{entity_type}/{entity_id}", response_model=dict, tags=["Audit Trail"])
async def reconstruct_entity_state(
    entity_type: EntityTypeEnum,
    entity_id: int,
    at_timestamp: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reconstruct entity state at a specific point in time

    Uses event sourcing to rebuild complete state from audit log
    """
    service = AuditService(db)
    result = service.reconstruct_entity_state(
        entity_type=entity_type,
        entity_id=entity_id,
        at_timestamp=at_timestamp
    )
    return result


# ==================== DATA LINEAGE ====================

@router.post("/data-lineage", response_model=DataLineageResponse, tags=["Data Lineage"])
async def track_data_transformation(
    lineage: DataLineageCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Track data transformation through pipeline stages

    Medallion Architecture:
    - Bronze: Raw data
    - Silver: Processed/cleaned data
    - Gold: Final/aggregated data
    """
    setup_audit_context(request, current_user, db)

    try:
        service = TraceabilityService(db)
        result = service.track_data_transformation(
            source_entity_type=lineage.source_entity_type,
            source_entity_id=lineage.source_entity_id,
            source_stage=lineage.source_stage,
            target_entity_type=lineage.target_entity_type,
            target_entity_id=lineage.target_entity_id,
            target_stage=lineage.target_stage,
            transformation_type=lineage.transformation_type,
            transformation_logic=lineage.transformation_logic,
            equipment_id=lineage.equipment_id,
            software_version=lineage.software_version,
            performed_by_id=current_user.id,
            data_quality_score=lineage.data_quality_score,
            validation_status=lineage.validation_status,
            metadata=lineage.metadata
        )
        return result
    finally:
        clear_audit_context()


@router.get("/data-lineage/{entity_type}/{entity_id}", response_model=DataLineagePathResponse, tags=["Data Lineage"])
async def get_data_lineage_path(
    entity_type: EntityTypeEnum,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete data lineage path from raw data to final report

    Traces: Bronze → Silver → Gold
    Shows all transformations, equipment used, and quality scores
    """
    service = TraceabilityService(db)
    path = service.get_data_lineage_path(
        entity_type=entity_type,
        entity_id=entity_id
    )
    return {
        "lineage_path": path,
        "total_stages": len(path)
    }


# ==================== REQUIREMENTS TRACEABILITY MATRIX ====================

@router.post("/requirements", response_model=RequirementResponse, tags=["Requirements Traceability"])
async def create_requirement(
    requirement: RequirementCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new requirement for traceability

    Requirements can be from:
    - ISO standards (17025, 9001, etc.)
    - Customer specifications
    - Regulatory requirements
    """
    setup_audit_context(request, current_user, db)

    try:
        service = TraceabilityService(db)
        result = service.create_requirement(
            requirement_number=requirement.requirement_number,
            requirement_title=requirement.requirement_title,
            requirement_description=requirement.requirement_description,
            requirement_source=requirement.requirement_source,
            requirement_category=requirement.requirement_category,
            requirement_priority=requirement.requirement_priority,
            compliance_standards=requirement.compliance_standards,
            created_by_id=current_user.id
        )
        return result
    finally:
        clear_audit_context()


@router.post("/requirements/link", response_model=RequirementResponse, tags=["Requirements Traceability"])
async def link_requirement_to_entity(
    link: RequirementLinkRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Link a requirement to evidence

    Evidence can be:
    - Documents (procedures, work instructions)
    - Test cases and results
    - Equipment calibrations
    - Training records
    """
    setup_audit_context(request, current_user, db)

    try:
        service = TraceabilityService(db)
        result = service.link_requirement_to_entity(
            requirement_id=link.requirement_id,
            entity_type=link.entity_type,
            entity_id=link.entity_id,
            verification_method=link.verification_method
        )
        return result
    finally:
        clear_audit_context()


@router.get("/requirements/coverage", response_model=RTMCoverageReport, tags=["Requirements Traceability"])
async def get_rtm_coverage_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate Requirements Traceability Matrix coverage report

    Shows:
    - Total requirements vs verified
    - Coverage percentage
    - Requirements by category
    - Gaps (requirements without evidence)
    """
    service = TraceabilityService(db)
    result = service.get_rtm_coverage_report()
    return result


# ==================== CHAIN OF CUSTODY ====================

@router.post("/chain-of-custody", response_model=ChainOfCustodyResponse, tags=["Chain of Custody"])
async def record_custody_event(
    custody: ChainOfCustodyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record a chain of custody event

    Events include:
    - Received, Transferred, Stored
    - Tested, Disposed, Returned

    Tracks:
    - Who transferred/received
    - Location movement
    - Condition before/after
    - Digital signatures
    - Seal numbers
    """
    setup_audit_context(request, current_user, db)

    try:
        service = TraceabilityService(db)
        result = service.record_custody_event(
            entity_type=custody.entity_type,
            entity_id=custody.entity_id,
            entity_identifier=custody.entity_identifier,
            event_type=custody.event_type,
            from_user_id=custody.from_user_id,
            to_user_id=custody.to_user_id,
            from_location=custody.from_location,
            to_location=custody.to_location,
            condition_before=custody.condition_before,
            condition_after=custody.condition_after,
            notes=custody.notes,
            metadata=custody.metadata
        )
        return result
    finally:
        clear_audit_context()


@router.get("/chain-of-custody/{entity_type}/{entity_id}", response_model=List[dict], tags=["Chain of Custody"])
async def get_custody_chain(
    entity_type: EntityTypeEnum,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete chain of custody for a sample or equipment

    Returns chronological list of all custody events
    """
    service = TraceabilityService(db)
    result = service.get_custody_chain(
        entity_type=entity_type,
        entity_id=entity_id
    )
    return result


# ==================== VERSION COMPARISON ====================

@router.post("/snapshots", response_model=SnapshotResponse, tags=["Version Comparison"])
async def create_entity_snapshot(
    snapshot: SnapshotCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a snapshot of entity state for version comparison

    Snapshots can be triggered:
    - Manually
    - On approval
    - Scheduled
    - Before deletion
    """
    setup_audit_context(request, current_user, db)

    try:
        service = TraceabilityService(db)
        result = service.create_snapshot(
            entity_type=snapshot.entity_type,
            entity_id=snapshot.entity_id,
            snapshot_data=snapshot.snapshot_data,
            snapshot_trigger=snapshot.snapshot_trigger,
            notes=snapshot.notes,
            created_by_id=current_user.id
        )
        return result
    finally:
        clear_audit_context()


@router.post("/snapshots/compare", response_model=VersionComparisonResponse, tags=["Version Comparison"])
async def compare_versions(
    comparison: VersionComparisonRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare two versions of an entity

    Returns:
    - Both version data
    - Side-by-side diff
    - Added, removed, and modified fields
    """
    service = TraceabilityService(db)
    result = service.compare_versions(
        entity_type=comparison.entity_type,
        entity_id=comparison.entity_id,
        version1=comparison.version1,
        version2=comparison.version2
    )
    return result


# ==================== COMPLIANCE EVIDENCE ====================

@router.post("/compliance-evidence", response_model=ComplianceEvidenceResponse, tags=["Compliance"])
async def create_compliance_evidence(
    evidence: ComplianceEvidenceCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create compliance evidence record

    Evidence types:
    - Calibration records
    - Training certificates
    - Audit reports
    - Test results
    - Quality certifications
    """
    setup_audit_context(request, current_user, db)

    try:
        service = TraceabilityService(db)
        result = service.create_compliance_evidence(
            evidence_number=evidence.evidence_number,
            evidence_type=evidence.evidence_type,
            title=evidence.title,
            description=evidence.description,
            compliance_standards=evidence.compliance_standards,
            evidence_date=evidence.evidence_date,
            expiry_date=evidence.expiry_date,
            entity_type=evidence.entity_type,
            entity_id=evidence.entity_id,
            document_references=evidence.document_references,
            created_by_id=current_user.id
        )
        return result
    finally:
        clear_audit_context()


@router.post("/compliance-reports", response_model=ComplianceReportResponse, tags=["Compliance"])
async def generate_compliance_report(
    report_request: ComplianceReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate compliance report for ISO 17025/9001 audits

    Filter by:
    - Standards (ISO 17025, ISO 9001, GLP, etc.)
    - Date range

    Returns:
    - Evidence by type
    - Evidence by standard
    - Summary statistics
    """
    service = TraceabilityService(db)
    result = service.get_compliance_report(
        standards=report_request.standards,
        start_date=report_request.start_date,
        end_date=report_request.end_date
    )
    return result
