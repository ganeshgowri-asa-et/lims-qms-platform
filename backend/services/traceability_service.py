"""
Traceability Service Layer
Provides graph-like querying for end-to-end traceability
"""
from typing import List, Dict, Any, Optional, Set, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime
from collections import deque, defaultdict
import json
import hashlib

from backend.models.traceability import (
    TraceabilityLink,
    AuditLog,
    DataLineage,
    RequirementTraceability,
    ChainOfCustody,
    EntitySnapshot,
    ComplianceEvidence,
    ImpactAnalysis,
    EntityTypeEnum,
    ActionTypeEnum,
    DataLineageStageEnum,
    CustodyEventTypeEnum,
    RequirementStatusEnum
)


class TraceabilityService:
    """Comprehensive traceability service with graph-like operations"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== DOCUMENT LINEAGE & TRACEABILITY ====================

    def get_forward_traceability(
        self,
        entity_type: EntityTypeEnum,
        entity_id: int,
        max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Get forward traceability (Level 1 → 2 → 3 → 4 → 5)
        Returns tree structure showing all downstream dependencies
        """
        visited = set()
        result = self._build_traceability_tree(
            entity_type, entity_id, "forward", visited, max_depth, current_depth=0
        )
        return result

    def get_backward_traceability(
        self,
        entity_type: EntityTypeEnum,
        entity_id: int,
        max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Get backward traceability (Level 5 → 4 → 3 → 2 → 1)
        Returns tree structure showing all upstream sources
        """
        visited = set()
        result = self._build_traceability_tree(
            entity_type, entity_id, "backward", visited, max_depth, current_depth=0
        )
        return result

    def _build_traceability_tree(
        self,
        entity_type: EntityTypeEnum,
        entity_id: int,
        direction: str,
        visited: Set[Tuple[str, int]],
        max_depth: int,
        current_depth: int
    ) -> Dict[str, Any]:
        """Recursively build traceability tree"""
        node_key = (entity_type.value, entity_id)

        if node_key in visited or current_depth >= max_depth:
            return {
                "entity_type": entity_type.value,
                "entity_id": entity_id,
                "circular_reference": node_key in visited,
                "max_depth_reached": current_depth >= max_depth
            }

        visited.add(node_key)

        # Get entity details
        entity_details = self._get_entity_details(entity_type, entity_id)

        # Get linked entities
        if direction == "forward":
            links = self.db.query(TraceabilityLink).filter(
                and_(
                    TraceabilityLink.source_entity_type == entity_type,
                    TraceabilityLink.source_entity_id == entity_id,
                    TraceabilityLink.is_deleted == False
                )
            ).all()
            children_key = "downstream"
        else:
            links = self.db.query(TraceabilityLink).filter(
                and_(
                    TraceabilityLink.target_entity_type == entity_type,
                    TraceabilityLink.target_entity_id == entity_id,
                    TraceabilityLink.is_deleted == False
                )
            ).all()
            children_key = "upstream"

        # Build children nodes
        children = []
        for link in links:
            if direction == "forward":
                child_type = link.target_entity_type
                child_id = link.target_entity_id
            else:
                child_type = link.source_entity_type
                child_id = link.source_entity_id

            child_node = self._build_traceability_tree(
                child_type, child_id, direction, visited, max_depth, current_depth + 1
            )
            child_node["link_type"] = link.link_type
            child_node["link_description"] = link.description
            children.append(child_node)

        return {
            "entity_type": entity_type.value,
            "entity_id": entity_id,
            "entity_details": entity_details,
            "depth": current_depth,
            children_key: children,
            "total_dependencies": len(children)
        }

    def get_bidirectional_links(
        self,
        entity_type: EntityTypeEnum,
        entity_id: int
    ) -> Dict[str, Any]:
        """Get both forward and backward links for navigation"""
        forward = self.get_forward_traceability(entity_type, entity_id, max_depth=1)
        backward = self.get_backward_traceability(entity_type, entity_id, max_depth=1)

        return {
            "entity": {
                "type": entity_type.value,
                "id": entity_id,
                "details": self._get_entity_details(entity_type, entity_id)
            },
            "downstream": forward.get("downstream", []),
            "upstream": backward.get("upstream", [])
        }

    def create_traceability_link(
        self,
        source_entity_type: EntityTypeEnum,
        source_entity_id: int,
        target_entity_type: EntityTypeEnum,
        target_entity_id: int,
        link_type: str,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        created_by_id: Optional[int] = None
    ) -> TraceabilityLink:
        """Create a new traceability link"""
        link = TraceabilityLink(
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            link_type=link_type,
            description=description,
            metadata=metadata,
            created_by_id=created_by_id
        )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link

    def get_impact_analysis(
        self,
        entity_type: EntityTypeEnum,
        entity_id: int,
        change_description: str
    ) -> Dict[str, Any]:
        """
        Analyze impact of changing this entity
        Returns all affected downstream entities
        """
        # Get all downstream entities
        forward_tree = self.get_forward_traceability(entity_type, entity_id, max_depth=10)

        # Flatten the tree to get all affected entities
        affected_entities = []
        self._flatten_tree(forward_tree, affected_entities)

        # Calculate impact scope
        total_affected = len(affected_entities)
        if total_affected == 0:
            impact_scope = "low"
        elif total_affected <= 5:
            impact_scope = "medium"
        elif total_affected <= 20:
            impact_scope = "high"
        else:
            impact_scope = "critical"

        return {
            "source_entity": {
                "type": entity_type.value,
                "id": entity_id
            },
            "change_description": change_description,
            "impact_scope": impact_scope,
            "total_affected": total_affected,
            "affected_entities": affected_entities,
            "impact_tree": forward_tree
        }

    def _flatten_tree(self, tree: Dict[str, Any], result: List[Dict], parent_path: str = ""):
        """Flatten traceability tree to list of entities"""
        if not tree:
            return

        entity_type = tree.get("entity_type")
        entity_id = tree.get("entity_id")

        if entity_type and entity_id:
            current_path = f"{parent_path}/{entity_type}:{entity_id}" if parent_path else f"{entity_type}:{entity_id}"
            result.append({
                "entity_type": entity_type,
                "entity_id": entity_id,
                "path": current_path,
                "depth": tree.get("depth", 0)
            })

        # Process children
        for child in tree.get("downstream", []) + tree.get("upstream", []):
            self._flatten_tree(child, result, current_path if entity_type else parent_path)

    # ==================== DATA LINEAGE ====================

    def track_data_transformation(
        self,
        source_entity_type: EntityTypeEnum,
        source_entity_id: int,
        source_stage: DataLineageStageEnum,
        target_entity_type: EntityTypeEnum,
        target_entity_id: int,
        target_stage: DataLineageStageEnum,
        transformation_type: str,
        transformation_logic: Optional[str] = None,
        equipment_id: Optional[int] = None,
        software_version: Optional[str] = None,
        performed_by_id: Optional[int] = None,
        data_quality_score: Optional[float] = None,
        validation_status: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> DataLineage:
        """Track data transformation through pipeline stages"""
        lineage = DataLineage(
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            source_stage=source_stage,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            target_stage=target_stage,
            transformation_type=transformation_type,
            transformation_logic=transformation_logic,
            equipment_id=equipment_id,
            software_version=software_version,
            performed_by_id=performed_by_id,
            data_quality_score=data_quality_score,
            validation_status=validation_status,
            metadata=metadata
        )
        self.db.add(lineage)
        self.db.commit()
        self.db.refresh(lineage)
        return lineage

    def get_data_lineage_path(
        self,
        entity_type: EntityTypeEnum,
        entity_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get complete data lineage path from raw data to final report
        Bronze → Silver → Gold
        """
        lineage_path = []

        # Start from current entity and trace backwards
        current_type = entity_type
        current_id = entity_id
        visited = set()

        while True:
            node_key = (current_type.value, current_id)
            if node_key in visited:
                break
            visited.add(node_key)

            # Get lineage record
            lineage = self.db.query(DataLineage).filter(
                and_(
                    DataLineage.target_entity_type == current_type,
                    DataLineage.target_entity_id == current_id
                )
            ).first()

            if not lineage:
                break

            lineage_path.insert(0, {
                "source": {
                    "entity_type": lineage.source_entity_type.value,
                    "entity_id": lineage.source_entity_id,
                    "stage": lineage.source_stage.value
                },
                "target": {
                    "entity_type": lineage.target_entity_type.value,
                    "entity_id": lineage.target_entity_id,
                    "stage": lineage.target_stage.value
                },
                "transformation_type": lineage.transformation_type,
                "transformation_logic": lineage.transformation_logic,
                "equipment_id": lineage.equipment_id,
                "software_version": lineage.software_version,
                "performed_by_id": lineage.performed_by_id,
                "performed_at": lineage.performed_at.isoformat() if lineage.performed_at else None,
                "data_quality_score": lineage.data_quality_score,
                "validation_status": lineage.validation_status
            })

            # Move to previous node
            current_type = lineage.source_entity_type
            current_id = lineage.source_entity_id

        return lineage_path

    # ==================== REQUIREMENTS TRACEABILITY MATRIX ====================

    def create_requirement(
        self,
        requirement_number: str,
        requirement_title: str,
        requirement_description: Optional[str] = None,
        requirement_source: Optional[str] = None,
        requirement_category: Optional[str] = None,
        requirement_priority: Optional[str] = None,
        compliance_standards: Optional[List[str]] = None,
        created_by_id: Optional[int] = None
    ) -> RequirementTraceability:
        """Create a new requirement for traceability"""
        requirement = RequirementTraceability(
            requirement_number=requirement_number,
            requirement_title=requirement_title,
            requirement_description=requirement_description,
            requirement_source=requirement_source,
            requirement_category=requirement_category,
            requirement_priority=requirement_priority,
            compliance_standards=compliance_standards,
            status=RequirementStatusEnum.DRAFT,
            created_by_id=created_by_id
        )
        self.db.add(requirement)
        self.db.commit()
        self.db.refresh(requirement)
        return requirement

    def link_requirement_to_entity(
        self,
        requirement_id: int,
        entity_type: EntityTypeEnum,
        entity_id: int,
        verification_method: Optional[str] = None
    ) -> RequirementTraceability:
        """Link a requirement to evidence (document, test, etc.)"""
        requirement = self.db.query(RequirementTraceability).filter(
            RequirementTraceability.id == requirement_id
        ).first()

        if requirement:
            requirement.linked_entity_type = entity_type
            requirement.linked_entity_id = entity_id
            requirement.verification_method = verification_method
            self.db.commit()
            self.db.refresh(requirement)

        return requirement

    def get_rtm_coverage_report(self) -> Dict[str, Any]:
        """
        Generate Requirements Traceability Matrix coverage report
        Shows which requirements have evidence and which don't
        """
        all_requirements = self.db.query(RequirementTraceability).filter(
            RequirementTraceability.is_deleted == False
        ).all()

        total = len(all_requirements)
        verified = sum(1 for r in all_requirements if r.verification_status == "verified")
        partially_verified = sum(1 for r in all_requirements if r.verification_status == "partially_verified")
        not_verified = sum(1 for r in all_requirements if r.verification_status == "not_verified" or r.verification_status is None)

        # Group by category
        by_category = defaultdict(list)
        for req in all_requirements:
            by_category[req.requirement_category or "Uncategorized"].append({
                "requirement_number": req.requirement_number,
                "title": req.requirement_title,
                "source": req.requirement_source,
                "priority": req.requirement_priority,
                "status": req.status.value,
                "verification_status": req.verification_status,
                "linked_entity": {
                    "type": req.linked_entity_type.value if req.linked_entity_type else None,
                    "id": req.linked_entity_id
                } if req.linked_entity_type else None
            })

        return {
            "summary": {
                "total_requirements": total,
                "verified": verified,
                "partially_verified": partially_verified,
                "not_verified": not_verified,
                "coverage_percentage": round((verified / total * 100) if total > 0 else 0, 2)
            },
            "by_category": dict(by_category),
            "gaps": [
                {
                    "requirement_number": req.requirement_number,
                    "title": req.requirement_title,
                    "priority": req.requirement_priority,
                    "source": req.requirement_source
                }
                for req in all_requirements
                if not req.verification_status or req.verification_status == "not_verified"
            ]
        }

    # ==================== CHAIN OF CUSTODY ====================

    def record_custody_event(
        self,
        entity_type: EntityTypeEnum,
        entity_id: int,
        entity_identifier: str,
        event_type: CustodyEventTypeEnum,
        from_user_id: Optional[int] = None,
        to_user_id: Optional[int] = None,
        from_location: Optional[str] = None,
        to_location: Optional[str] = None,
        condition_before: Optional[str] = None,
        condition_after: Optional[str] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> ChainOfCustody:
        """Record a chain of custody event"""
        custody = ChainOfCustody(
            entity_type=entity_type,
            entity_id=entity_id,
            entity_identifier=entity_identifier,
            event_type=event_type,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            from_location=from_location,
            to_location=to_location,
            condition_before=condition_before,
            condition_after=condition_after,
            notes=notes,
            metadata=metadata
        )
        self.db.add(custody)
        self.db.commit()
        self.db.refresh(custody)
        return custody

    def get_custody_chain(
        self,
        entity_type: EntityTypeEnum,
        entity_id: int
    ) -> List[Dict[str, Any]]:
        """Get complete chain of custody for an entity"""
        custody_events = self.db.query(ChainOfCustody).filter(
            and_(
                ChainOfCustody.entity_type == entity_type,
                ChainOfCustody.entity_id == entity_id,
                ChainOfCustody.is_deleted == False
            )
        ).order_by(ChainOfCustody.event_timestamp.asc()).all()

        return [
            {
                "event_id": event.id,
                "event_type": event.event_type.value,
                "timestamp": event.event_timestamp.isoformat(),
                "from_user_id": event.from_user_id,
                "to_user_id": event.to_user_id,
                "from_location": event.from_location,
                "to_location": event.to_location,
                "condition_before": event.condition_before,
                "condition_after": event.condition_after,
                "integrity_check": event.integrity_check,
                "notes": event.notes
            }
            for event in custody_events
        ]

    # ==================== VERSION COMPARISON ====================

    def create_snapshot(
        self,
        entity_type: EntityTypeEnum,
        entity_id: int,
        snapshot_data: Dict[str, Any],
        snapshot_trigger: str = "manual",
        notes: Optional[str] = None,
        created_by_id: Optional[int] = None
    ) -> EntitySnapshot:
        """Create a snapshot of entity state for version comparison"""
        # Get version number
        last_snapshot = self.db.query(EntitySnapshot).filter(
            and_(
                EntitySnapshot.entity_type == entity_type,
                EntitySnapshot.entity_id == entity_id
            )
        ).order_by(EntitySnapshot.version_number.desc()).first()

        version_number = (last_snapshot.version_number + 1) if last_snapshot else 1

        # Calculate hash
        snapshot_json = json.dumps(snapshot_data, sort_keys=True)
        snapshot_hash = hashlib.sha256(snapshot_json.encode()).hexdigest()

        # Calculate diff from previous version
        diff_from_previous = None
        if last_snapshot:
            diff_from_previous = self._calculate_diff(
                last_snapshot.snapshot_data,
                snapshot_data
            )

        snapshot = EntitySnapshot(
            entity_type=entity_type,
            entity_id=entity_id,
            version_number=version_number,
            snapshot_data=snapshot_data,
            snapshot_hash=snapshot_hash,
            snapshot_size=len(snapshot_json),
            diff_from_previous=diff_from_previous,
            snapshot_trigger=snapshot_trigger,
            notes=notes,
            created_by_id=created_by_id
        )

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def compare_versions(
        self,
        entity_type: EntityTypeEnum,
        entity_id: int,
        version1: int,
        version2: int
    ) -> Dict[str, Any]:
        """Compare two versions of an entity"""
        snapshot1 = self.db.query(EntitySnapshot).filter(
            and_(
                EntitySnapshot.entity_type == entity_type,
                EntitySnapshot.entity_id == entity_id,
                EntitySnapshot.version_number == version1
            )
        ).first()

        snapshot2 = self.db.query(EntitySnapshot).filter(
            and_(
                EntitySnapshot.entity_type == entity_type,
                EntitySnapshot.entity_id == entity_id,
                EntitySnapshot.version_number == version2
            )
        ).first()

        if not snapshot1 or not snapshot2:
            return {"error": "One or both versions not found"}

        diff = self._calculate_diff(snapshot1.snapshot_data, snapshot2.snapshot_data)

        return {
            "version1": {
                "version_number": version1,
                "created_at": snapshot1.created_at.isoformat(),
                "created_by_id": snapshot1.created_by_id,
                "data": snapshot1.snapshot_data
            },
            "version2": {
                "version_number": version2,
                "created_at": snapshot2.created_at.isoformat(),
                "created_by_id": snapshot2.created_by_id,
                "data": snapshot2.snapshot_data
            },
            "diff": diff
        }

    def _calculate_diff(self, old_data: Dict, new_data: Dict) -> Dict[str, Any]:
        """Calculate difference between two data dictionaries"""
        diff = {
            "added": {},
            "removed": {},
            "modified": {}
        }

        # Find added and modified
        for key, new_value in new_data.items():
            if key not in old_data:
                diff["added"][key] = new_value
            elif old_data[key] != new_value:
                diff["modified"][key] = {
                    "old": old_data[key],
                    "new": new_value
                }

        # Find removed
        for key, old_value in old_data.items():
            if key not in new_data:
                diff["removed"][key] = old_value

        return diff

    # ==================== COMPLIANCE EVIDENCE ====================

    def create_compliance_evidence(
        self,
        evidence_number: str,
        evidence_type: str,
        title: str,
        compliance_standards: List[str],
        evidence_date: datetime,
        description: Optional[str] = None,
        entity_type: Optional[EntityTypeEnum] = None,
        entity_id: Optional[int] = None,
        expiry_date: Optional[datetime] = None,
        document_references: Optional[List[int]] = None,
        created_by_id: Optional[int] = None
    ) -> ComplianceEvidence:
        """Create compliance evidence record"""
        evidence = ComplianceEvidence(
            evidence_number=evidence_number,
            evidence_type=evidence_type,
            title=title,
            description=description,
            compliance_standards=compliance_standards,
            evidence_date=evidence_date,
            expiry_date=expiry_date,
            entity_type=entity_type,
            entity_id=entity_id,
            document_references=document_references,
            status="valid",
            created_by_id=created_by_id
        )
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def get_compliance_report(
        self,
        standards: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate compliance report for specified standards"""
        query = self.db.query(ComplianceEvidence).filter(
            ComplianceEvidence.is_deleted == False
        )

        if standards:
            # Filter by standards (JSON contains any of the specified standards)
            query = query.filter(
                ComplianceEvidence.compliance_standards.contains(standards)
            )

        if start_date:
            query = query.filter(ComplianceEvidence.evidence_date >= start_date)

        if end_date:
            query = query.filter(ComplianceEvidence.evidence_date <= end_date)

        evidence_records = query.all()

        # Group by evidence type
        by_type = defaultdict(list)
        by_standard = defaultdict(list)

        for evidence in evidence_records:
            by_type[evidence.evidence_type].append({
                "evidence_number": evidence.evidence_number,
                "title": evidence.title,
                "evidence_date": evidence.evidence_date.isoformat(),
                "expiry_date": evidence.expiry_date.isoformat() if evidence.expiry_date else None,
                "status": evidence.status,
                "standards": evidence.compliance_standards
            })

            for standard in (evidence.compliance_standards or []):
                by_standard[standard].append(evidence.evidence_number)

        return {
            "report_generated": datetime.utcnow().isoformat(),
            "filters": {
                "standards": standards,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "summary": {
                "total_evidence": len(evidence_records),
                "valid": sum(1 for e in evidence_records if e.status == "valid"),
                "expired": sum(1 for e in evidence_records if e.status == "expired"),
                "superseded": sum(1 for e in evidence_records if e.status == "superseded")
            },
            "by_type": dict(by_type),
            "by_standard": dict(by_standard)
        }

    # ==================== HELPER METHODS ====================

    def _get_entity_details(self, entity_type: EntityTypeEnum, entity_id: int) -> Optional[Dict]:
        """Get entity details from appropriate table"""
        # Import models based on entity type
        from backend.models.document import Document
        from backend.models.form import FormRecord
        from backend.models.workflow import Project, Task
        from backend.models.procurement import Equipment, PurchaseOrder
        from backend.models.quality import NonConformance, CAPA, Audit as QualityAudit

        model_map = {
            EntityTypeEnum.DOCUMENT: Document,
            EntityTypeEnum.FORM_RECORD: FormRecord,
            EntityTypeEnum.PROJECT: Project,
            EntityTypeEnum.TASK: Task,
            EntityTypeEnum.EQUIPMENT: Equipment,
            EntityTypeEnum.PURCHASE_ORDER: PurchaseOrder,
            EntityTypeEnum.NON_CONFORMANCE: NonConformance,
            EntityTypeEnum.CAPA: CAPA,
            EntityTypeEnum.AUDIT: QualityAudit,
        }

        model = model_map.get(entity_type)
        if not model:
            return None

        entity = self.db.query(model).filter(model.id == entity_id).first()
        if not entity:
            return None

        # Return basic info
        return {
            "id": entity.id,
            "name": getattr(entity, 'title', None) or getattr(entity, 'name', None) or getattr(entity, 'number', None),
            "created_at": entity.created_at.isoformat() if hasattr(entity, 'created_at') else None,
            "status": getattr(entity, 'status', None)
        }
