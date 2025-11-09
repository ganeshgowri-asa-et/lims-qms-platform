"""
Audit Service Layer
Implements event sourcing and blockchain-inspired immutable audit trail
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from datetime import datetime
import hashlib
import json

from backend.models.traceability import (
    AuditLog,
    EntityTypeEnum,
    ActionTypeEnum
)


class AuditService:
    """Immutable, event-sourced audit trail service"""

    def __init__(self, db: Session):
        self.db = db

    def log_event(
        self,
        user_id: Optional[int],
        entity_type: EntityTypeEnum,
        entity_id: int,
        action: ActionTypeEnum,
        description: Optional[str] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        location: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> AuditLog:
        """
        Log an audit event with blockchain-inspired immutability
        Creates an event chain where each event references the previous one
        """
        # Get the next sequence number
        last_event = self.db.query(AuditLog).order_by(
            AuditLog.event_sequence.desc()
        ).first()

        event_sequence = (last_event.event_sequence + 1) if last_event else 1

        # Get previous checksum for chaining
        previous_checksum = last_event.checksum if last_event else None

        # Create event data for hashing
        event_data = {
            "event_sequence": event_sequence,
            "user_id": user_id,
            "entity_type": entity_type.value,
            "entity_id": entity_id,
            "action": action.value,
            "description": description,
            "old_values": old_values,
            "new_values": new_values,
            "timestamp": datetime.utcnow().isoformat(),
            "previous_checksum": previous_checksum
        }

        # Calculate checksum (SHA-256)
        event_json = json.dumps(event_data, sort_keys=True)
        checksum = hashlib.sha256(event_json.encode()).hexdigest()

        # Create audit log entry
        audit_log = AuditLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            description=description,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            location=location,
            reason=reason,
            metadata=metadata,
            event_sequence=event_sequence,
            checksum=checksum,
            previous_checksum=previous_checksum
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        return audit_log

    def verify_audit_chain_integrity(
        self,
        start_sequence: Optional[int] = None,
        end_sequence: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Verify the integrity of the audit chain
        Ensures no events have been tampered with
        """
        query = self.db.query(AuditLog).order_by(AuditLog.event_sequence.asc())

        if start_sequence:
            query = query.filter(AuditLog.event_sequence >= start_sequence)
        if end_sequence:
            query = query.filter(AuditLog.event_sequence <= end_sequence)

        events = query.all()

        integrity_issues = []
        previous_checksum = None

        for event in events:
            # Verify checksum chain
            if event.previous_checksum != previous_checksum:
                integrity_issues.append({
                    "event_sequence": event.event_sequence,
                    "issue": "checksum_chain_broken",
                    "expected_previous": previous_checksum,
                    "actual_previous": event.previous_checksum
                })

            # Verify event checksum
            event_data = {
                "event_sequence": event.event_sequence,
                "user_id": event.user_id,
                "entity_type": event.entity_type.value,
                "entity_id": event.entity_id,
                "action": event.action.value,
                "description": event.description,
                "old_values": event.old_values,
                "new_values": event.new_values,
                "timestamp": event.created_at.isoformat(),
                "previous_checksum": event.previous_checksum
            }

            event_json = json.dumps(event_data, sort_keys=True)
            calculated_checksum = hashlib.sha256(event_json.encode()).hexdigest()

            if calculated_checksum != event.checksum:
                integrity_issues.append({
                    "event_sequence": event.event_sequence,
                    "issue": "checksum_mismatch",
                    "expected_checksum": event.checksum,
                    "calculated_checksum": calculated_checksum
                })

            previous_checksum = event.checksum

        return {
            "total_events_checked": len(events),
            "integrity_intact": len(integrity_issues) == 0,
            "issues_found": len(integrity_issues),
            "issues": integrity_issues
        }

    def get_entity_audit_history(
        self,
        entity_type: EntityTypeEnum,
        entity_id: int,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get complete audit history for an entity"""
        query = self.db.query(AuditLog).filter(
            and_(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id
            )
        ).order_by(AuditLog.created_at.desc())

        if limit:
            query = query.limit(limit)

        events = query.all()

        return [
            {
                "event_sequence": event.event_sequence,
                "action": event.action.value,
                "user_id": event.user_id,
                "timestamp": event.created_at.isoformat(),
                "description": event.description,
                "old_values": event.old_values,
                "new_values": event.new_values,
                "ip_address": event.ip_address,
                "location": event.location,
                "reason": event.reason,
                "checksum": event.checksum
            }
            for event in events
        ]

    def search_audit_logs(
        self,
        user_id: Optional[int] = None,
        entity_type: Optional[EntityTypeEnum] = None,
        entity_id: Optional[int] = None,
        action: Optional[ActionTypeEnum] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search audit logs with filters
        Supports pagination and multiple search criteria
        """
        query = self.db.query(AuditLog)

        # Apply filters
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        if ip_address:
            query = query.filter(AuditLog.ip_address == ip_address)

        # Get total count
        total = query.count()

        # Apply pagination
        events = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": [
                {
                    "event_sequence": event.event_sequence,
                    "user_id": event.user_id,
                    "entity_type": event.entity_type.value,
                    "entity_id": event.entity_id,
                    "action": event.action.value,
                    "timestamp": event.created_at.isoformat(),
                    "description": event.description,
                    "old_values": event.old_values,
                    "new_values": event.new_values,
                    "ip_address": event.ip_address,
                    "location": event.location,
                    "reason": event.reason
                }
                for event in events
            ]
        }

    def export_audit_log(
        self,
        entity_type: Optional[EntityTypeEnum] = None,
        entity_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export audit logs for compliance audits
        Supports multiple formats (JSON, CSV-ready)
        """
        query = self.db.query(AuditLog).order_by(AuditLog.event_sequence.asc())

        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        events = query.all()

        # Format for export
        export_data = []
        for event in events:
            export_data.append({
                "Event Sequence": event.event_sequence,
                "User ID": event.user_id,
                "Entity Type": event.entity_type.value,
                "Entity ID": event.entity_id,
                "Action": event.action.value,
                "Timestamp (UTC)": event.created_at.isoformat(),
                "Description": event.description,
                "Old Values": json.dumps(event.old_values) if event.old_values else None,
                "New Values": json.dumps(event.new_values) if event.new_values else None,
                "IP Address": event.ip_address,
                "User Agent": event.user_agent,
                "Location": event.location,
                "Reason for Change": event.reason,
                "Checksum": event.checksum,
                "Previous Checksum": event.previous_checksum
            })

        return {
            "export_generated": datetime.utcnow().isoformat(),
            "total_events": len(export_data),
            "format": format,
            "data": export_data
        }

    def reconstruct_entity_state(
        self,
        entity_type: EntityTypeEnum,
        entity_id: int,
        at_timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Reconstruct entity state at a specific point in time
        Uses event sourcing to rebuild state from audit log
        """
        query = self.db.query(AuditLog).filter(
            and_(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id
            )
        ).order_by(AuditLog.created_at.asc())

        if at_timestamp:
            query = query.filter(AuditLog.created_at <= at_timestamp)

        events = query.all()

        if not events:
            return {"error": "No events found for this entity"}

        # Reconstruct state
        state = {}
        for event in events:
            if event.action == ActionTypeEnum.CREATE:
                state = event.new_values or {}
            elif event.action == ActionTypeEnum.UPDATE:
                if event.new_values:
                    state.update(event.new_values)
            elif event.action == ActionTypeEnum.DELETE:
                state["_deleted"] = True
                state["_deleted_at"] = event.created_at.isoformat()

        return {
            "entity_type": entity_type.value,
            "entity_id": entity_id,
            "reconstructed_at": at_timestamp.isoformat() if at_timestamp else "latest",
            "total_events_applied": len(events),
            "state": state
        }

    def get_user_activity_summary(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get summary of user activity for audit purposes"""
        query = self.db.query(AuditLog).filter(AuditLog.user_id == user_id)

        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        events = query.all()

        # Group by action type
        actions_summary = {}
        for action_type in ActionTypeEnum:
            count = sum(1 for e in events if e.action == action_type)
            if count > 0:
                actions_summary[action_type.value] = count

        # Group by entity type
        entities_summary = {}
        for entity_type in EntityTypeEnum:
            count = sum(1 for e in events if e.entity_type == entity_type)
            if count > 0:
                entities_summary[entity_type.value] = count

        return {
            "user_id": user_id,
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "total_actions": len(events),
            "by_action_type": actions_summary,
            "by_entity_type": entities_summary,
            "first_activity": events[0].created_at.isoformat() if events else None,
            "last_activity": events[-1].created_at.isoformat() if events else None
        }
