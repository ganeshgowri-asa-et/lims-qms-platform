"""
SQLAlchemy Event Listeners for Automatic Audit Logging
Hooks into ORM lifecycle events to automatically track all changes
"""
from sqlalchemy import event
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
from contextvars import ContextVar

from backend.models.base import BaseModel
from backend.models.traceability import EntityTypeEnum, ActionTypeEnum
from backend.services.audit_service import AuditService

# Context variables to store request context across the call stack
audit_context_user_id: ContextVar[Optional[int]] = ContextVar('audit_context_user_id', default=None)
audit_context_ip_address: ContextVar[Optional[str]] = ContextVar('audit_context_ip_address', default=None)
audit_context_user_agent: ContextVar[Optional[str]] = ContextVar('audit_context_user_agent', default=None)
audit_context_session_id: ContextVar[Optional[str]] = ContextVar('audit_context_session_id', default=None)
audit_context_location: ContextVar[Optional[str]] = ContextVar('audit_context_location', default=None)
audit_context_reason: ContextVar[Optional[str]] = ContextVar('audit_context_reason', default=None)


def set_audit_context(
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    session_id: Optional[str] = None,
    location: Optional[str] = None,
    reason: Optional[str] = None
):
    """Set audit context for the current request"""
    if user_id is not None:
        audit_context_user_id.set(user_id)
    if ip_address is not None:
        audit_context_ip_address.set(ip_address)
    if user_agent is not None:
        audit_context_user_agent.set(user_agent)
    if session_id is not None:
        audit_context_session_id.set(session_id)
    if location is not None:
        audit_context_location.set(location)
    if reason is not None:
        audit_context_reason.set(reason)


def clear_audit_context():
    """Clear audit context"""
    audit_context_user_id.set(None)
    audit_context_ip_address.set(None)
    audit_context_user_agent.set(None)
    audit_context_session_id.set(None)
    audit_context_location.set(None)
    audit_context_reason.set(None)


# Map table names to entity types
TABLE_TO_ENTITY_TYPE = {
    'documents': EntityTypeEnum.DOCUMENT,
    'form_records': EntityTypeEnum.FORM_RECORD,
    'projects': EntityTypeEnum.PROJECT,
    'tasks': EntityTypeEnum.TASK,
    'equipment': EntityTypeEnum.EQUIPMENT,
    'calibrations': EntityTypeEnum.CALIBRATION,
    'purchase_orders': EntityTypeEnum.PURCHASE_ORDER,
    'orders': EntityTypeEnum.CUSTOMER_ORDER,
    'non_conformances': EntityTypeEnum.NON_CONFORMANCE,
    'capas': EntityTypeEnum.CAPA,
    'audits': EntityTypeEnum.AUDIT,
    'vendors': EntityTypeEnum.VENDOR,
    'employees': EntityTypeEnum.EMPLOYEE,
    'trainings': EntityTypeEnum.TRAINING,
}


def get_entity_type_from_model(model) -> Optional[EntityTypeEnum]:
    """Determine entity type from model"""
    table_name = model.__tablename__ if hasattr(model, '__tablename__') else None
    return TABLE_TO_ENTITY_TYPE.get(table_name)


def serialize_model_data(obj) -> Dict[str, Any]:
    """Serialize model instance to dictionary for audit log"""
    data = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name, None)
        # Convert non-JSON-serializable types
        if hasattr(value, 'isoformat'):  # datetime
            value = value.isoformat()
        elif hasattr(value, 'value'):  # enum
            value = value.value
        elif value is not None and not isinstance(value, (str, int, float, bool, dict, list)):
            value = str(value)
        data[column.name] = value
    return data


def before_insert_listener(mapper, connection, target):
    """
    Listener for before insert events
    Store original state for audit logging after commit
    """
    if not isinstance(target, BaseModel):
        return

    # Don't audit the audit log itself
    if hasattr(target, '__tablename__') and target.__tablename__ in ['audit_logs', 'traceability_links',
                                                                       'data_lineage', 'entity_snapshots',
                                                                       'chain_of_custody', 'requirement_traceability',
                                                                       'compliance_evidence', 'impact_analysis']:
        return

    # Store data for after_insert
    if not hasattr(target, '_audit_data'):
        target._audit_data = {
            'action': 'INSERT',
            'new_values': None  # Will be set in after_insert
        }


def after_insert_listener(mapper, connection, target):
    """
    Listener for after insert events
    Log CREATE action to audit log
    """
    if not isinstance(target, BaseModel):
        return

    # Don't audit the audit log itself
    if hasattr(target, '__tablename__') and target.__tablename__ in ['audit_logs', 'traceability_links',
                                                                       'data_lineage', 'entity_snapshots',
                                                                       'chain_of_custody', 'requirement_traceability',
                                                                       'compliance_evidence', 'impact_analysis']:
        return

    entity_type = get_entity_type_from_model(target)
    if not entity_type:
        return

    # Serialize new values
    new_values = serialize_model_data(target)

    # Get audit context
    user_id = audit_context_user_id.get()
    ip_address = audit_context_ip_address.get()
    user_agent = audit_context_user_agent.get()
    session_id = audit_context_session_id.get()
    location = audit_context_location.get()
    reason = audit_context_reason.get()

    # Create new session for audit logging (to avoid conflicts)
    from backend.core.database import SessionLocal
    audit_db = SessionLocal()
    try:
        audit_service = AuditService(audit_db)
        audit_service.log_event(
            user_id=user_id or getattr(target, 'created_by_id', None),
            entity_type=entity_type,
            entity_id=target.id,
            action=ActionTypeEnum.CREATE,
            description=f"Created {entity_type.value} #{target.id}",
            old_values=None,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            location=location,
            reason=reason
        )
    finally:
        audit_db.close()


def before_update_listener(mapper, connection, target):
    """
    Listener for before update events
    Capture old values before the update
    """
    if not isinstance(target, BaseModel):
        return

    # Don't audit the audit log itself
    if hasattr(target, '__tablename__') and target.__tablename__ in ['audit_logs', 'traceability_links',
                                                                       'data_lineage', 'entity_snapshots',
                                                                       'chain_of_custody', 'requirement_traceability',
                                                                       'compliance_evidence', 'impact_analysis']:
        return

    # Get current state from database
    from sqlalchemy import inspect
    from backend.core.database import SessionLocal

    db = SessionLocal()
    try:
        old_instance = db.query(target.__class__).filter_by(id=target.id).first()
        if old_instance:
            old_values = serialize_model_data(old_instance)
        else:
            old_values = None

        # Store for after_update
        if not hasattr(target, '_audit_data'):
            target._audit_data = {}

        target._audit_data['old_values'] = old_values
        target._audit_data['action'] = 'UPDATE'
    finally:
        db.close()


def after_update_listener(mapper, connection, target):
    """
    Listener for after update events
    Log UPDATE action to audit log with old and new values
    """
    if not isinstance(target, BaseModel):
        return

    # Don't audit the audit log itself
    if hasattr(target, '__tablename__') and target.__tablename__ in ['audit_logs', 'traceability_links',
                                                                       'data_lineage', 'entity_snapshots',
                                                                       'chain_of_custody', 'requirement_traceability',
                                                                       'compliance_evidence', 'impact_analysis']:
        return

    entity_type = get_entity_type_from_model(target)
    if not entity_type:
        return

    # Get old values from before_update
    old_values = getattr(target, '_audit_data', {}).get('old_values')

    # Serialize new values
    new_values = serialize_model_data(target)

    # Calculate what changed
    changed_fields = {}
    if old_values and new_values:
        for key in new_values:
            if key in old_values and old_values[key] != new_values[key]:
                changed_fields[key] = {
                    'old': old_values[key],
                    'new': new_values[key]
                }

    # Only log if something actually changed (excluding updated_at)
    if changed_fields and len([k for k in changed_fields.keys() if k not in ['updated_at', 'updated_by_id']]) > 0:
        # Get audit context
        user_id = audit_context_user_id.get()
        ip_address = audit_context_ip_address.get()
        user_agent = audit_context_user_agent.get()
        session_id = audit_context_session_id.get()
        location = audit_context_location.get()
        reason = audit_context_reason.get()

        # Create new session for audit logging
        from backend.core.database import SessionLocal
        audit_db = SessionLocal()
        try:
            audit_service = AuditService(audit_db)

            # Build description of changes
            field_names = list(changed_fields.keys())[:3]  # First 3 fields
            description = f"Updated {entity_type.value} #{target.id} - Changed: {', '.join(field_names)}"
            if len(changed_fields) > 3:
                description += f" and {len(changed_fields) - 3} more"

            audit_service.log_event(
                user_id=user_id or getattr(target, 'updated_by_id', None),
                entity_type=entity_type,
                entity_id=target.id,
                action=ActionTypeEnum.UPDATE,
                description=description,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                location=location,
                reason=reason,
                metadata={'changed_fields': changed_fields}
            )
        finally:
            audit_db.close()


def before_delete_listener(mapper, connection, target):
    """
    Listener for before delete events
    Capture state before deletion
    """
    if not isinstance(target, BaseModel):
        return

    # Don't audit the audit log itself
    if hasattr(target, '__tablename__') and target.__tablename__ in ['audit_logs', 'traceability_links',
                                                                       'data_lineage', 'entity_snapshots',
                                                                       'chain_of_custody', 'requirement_traceability',
                                                                       'compliance_evidence', 'impact_analysis']:
        return

    # Serialize current state
    old_values = serialize_model_data(target)

    # Store for after_delete
    if not hasattr(target, '_audit_data'):
        target._audit_data = {}

    target._audit_data['old_values'] = old_values
    target._audit_data['action'] = 'DELETE'


def after_delete_listener(mapper, connection, target):
    """
    Listener for after delete events
    Log DELETE action to audit log
    """
    if not isinstance(target, BaseModel):
        return

    # Don't audit the audit log itself
    if hasattr(target, '__tablename__') and target.__tablename__ in ['audit_logs', 'traceability_links',
                                                                       'data_lineage', 'entity_snapshots',
                                                                       'chain_of_custody', 'requirement_traceability',
                                                                       'compliance_evidence', 'impact_analysis']:
        return

    entity_type = get_entity_type_from_model(target)
    if not entity_type:
        return

    # Get old values from before_delete
    old_values = getattr(target, '_audit_data', {}).get('old_values')

    # Get audit context
    user_id = audit_context_user_id.get()
    ip_address = audit_context_ip_address.get()
    user_agent = audit_context_user_agent.get()
    session_id = audit_context_session_id.get()
    location = audit_context_location.get()
    reason = audit_context_reason.get()

    # Create new session for audit logging
    from backend.core.database import SessionLocal
    audit_db = SessionLocal()
    try:
        audit_service = AuditService(audit_db)
        audit_service.log_event(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=target.id,
            action=ActionTypeEnum.DELETE,
            description=f"Deleted {entity_type.value} #{target.id}",
            old_values=old_values,
            new_values=None,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            location=location,
            reason=reason
        )
    finally:
        audit_db.close()


def register_audit_listeners():
    """
    Register all audit event listeners
    Call this function during application startup
    """
    # Import all models that need auditing
    from backend.models.document import Document
    from backend.models.form import FormRecord
    from backend.models.workflow import Project, Task
    from backend.models.procurement import Equipment, Calibration, PurchaseOrder
    from backend.models.quality import NonConformance, CAPA, Audit as QualityAudit
    from backend.models.procurement import Vendor
    from backend.models.hr import Employee, Training

    models_to_audit = [
        Document,
        FormRecord,
        Project,
        Task,
        Equipment,
        Calibration,
        PurchaseOrder,
        NonConformance,
        CAPA,
        QualityAudit,
        Vendor,
        Employee,
        Training,
    ]

    for model in models_to_audit:
        # Register listeners
        event.listen(model, 'before_insert', before_insert_listener)
        event.listen(model, 'after_insert', after_insert_listener)
        event.listen(model, 'before_update', before_update_listener)
        event.listen(model, 'after_update', after_update_listener)
        event.listen(model, 'before_delete', before_delete_listener)
        event.listen(model, 'after_delete', after_delete_listener)

    print("✓ Audit event listeners registered for automatic change tracking")
