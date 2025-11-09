"""
Traceability and Audit Trail models
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
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
    """Comprehensive audit trail for all actions"""
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
    metadata = Column(JSON, nullable=True)
