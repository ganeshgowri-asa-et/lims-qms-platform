"""
Base models for common functionality
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base
import enum


class WorkflowStatus(str, enum.Enum):
    """Workflow status for Doer-Checker-Approver pattern"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    CHECKED = "checked"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUIRED = "revision_required"


class UserRole(str, enum.Enum):
    """User roles in the system"""
    ADMIN = "admin"
    QA_MANAGER = "qa_manager"
    CALIBRATION_ENGINEER = "calibration_engineer"
    TECHNICIAN = "technician"
    DOER = "doer"
    CHECKER = "checker"
    APPROVER = "approver"
    VIEWER = "viewer"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    phone_number = Column(String(20))
    department = Column(String(100))
    employee_id = Column(String(50), unique=True)

    # Digital signature
    signature_data = Column(Text)  # Base64 encoded signature image
    signature_cert = Column(Text)  # Digital certificate

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"))
    updated_by_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id], remote_side=[id])
    updated_by = relationship("User", foreign_keys=[updated_by_id], remote_side=[id])


class AuditLog(Base):
    """Audit log for tracking all changes"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False, index=True)
    record_id = Column(Integer, nullable=False, index=True)
    action = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE, APPROVE, REJECT
    old_values = Column(JSON)
    new_values = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    comments = Column(Text)

    # Relationships
    user = relationship("User")


class DocumentReference(Base):
    """Document references for traceability to Level 1/2/3 docs"""
    __tablename__ = "document_references"

    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String(50), nullable=False)  # SOP, QSF, WI, etc.
    document_number = Column(String(50), nullable=False, index=True)
    document_title = Column(String(255), nullable=False)
    document_version = Column(String(20), nullable=False)
    document_url = Column(String(500))
    effective_date = Column(DateTime(timezone=True))
    review_date = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)

    # Linked to which table/record
    linked_table = Column(String(100))
    linked_record_id = Column(Integer)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    created_by = relationship("User")


class WorkflowRecord(Base):
    """Generic workflow tracking for Doer-Checker-Approver pattern"""
    __tablename__ = "workflow_records"

    id = Column(Integer, primary_key=True, index=True)

    # Link to actual record
    table_name = Column(String(100), nullable=False, index=True)
    record_id = Column(Integer, nullable=False, index=True)

    # Workflow status
    status = Column(SQLEnum(WorkflowStatus), nullable=False, default=WorkflowStatus.DRAFT)

    # Doer-Checker-Approver
    doer_id = Column(Integer, ForeignKey("users.id"))
    doer_timestamp = Column(DateTime(timezone=True))
    doer_signature = Column(Text)
    doer_comments = Column(Text)

    checker_id = Column(Integer, ForeignKey("users.id"))
    checker_timestamp = Column(DateTime(timezone=True))
    checker_signature = Column(Text)
    checker_comments = Column(Text)

    approver_id = Column(Integer, ForeignKey("users.id"))
    approver_timestamp = Column(DateTime(timezone=True))
    approver_signature = Column(Text)
    approver_comments = Column(Text)

    # Rejection handling
    rejected_by_id = Column(Integer, ForeignKey("users.id"))
    rejection_timestamp = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    doer = relationship("User", foreign_keys=[doer_id])
    checker = relationship("User", foreign_keys=[checker_id])
    approver = relationship("User", foreign_keys=[approver_id])
    rejected_by = relationship("User", foreign_keys=[rejected_by_id])
