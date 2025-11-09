"""Database models for LIMS QMS Platform - NC and CAPA Management."""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey,
    Enum, Boolean, JSON, Numeric, Date
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


Base = declarative_base()


class NCStatus(str, enum.Enum):
    """Non-Conformance status enumeration."""
    OPEN = "open"
    UNDER_INVESTIGATION = "under_investigation"
    RCA_IN_PROGRESS = "rca_in_progress"
    CAPA_ASSIGNED = "capa_assigned"
    CLOSED = "closed"
    VERIFIED = "verified"


class NCSeverity(str, enum.Enum):
    """Non-Conformance severity levels."""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class NCSource(str, enum.Enum):
    """Source of Non-Conformance."""
    INTERNAL_AUDIT = "internal_audit"
    CUSTOMER_COMPLAINT = "customer_complaint"
    PROCESS_MONITORING = "process_monitoring"
    CALIBRATION = "calibration"
    TESTING = "testing"
    SUPPLIER = "supplier"
    EXTERNAL_AUDIT = "external_audit"
    OTHER = "other"


class CAPAType(str, enum.Enum):
    """CAPA Action type."""
    CORRECTIVE = "corrective"
    PREVENTIVE = "preventive"


class CAPAStatus(str, enum.Enum):
    """CAPA Action status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CLOSED = "closed"


class RCAMethod(str, enum.Enum):
    """Root Cause Analysis methodology."""
    FIVE_WHY = "5-why"
    FISHBONE = "fishbone"
    PARETO = "pareto"
    FAULT_TREE = "fault_tree"
    OTHER = "other"


class NonConformance(Base):
    """Non-Conformance records table."""

    __tablename__ = "nonconformances"

    id = Column(Integer, primary_key=True, index=True)
    nc_number = Column(String(50), unique=True, nullable=False, index=True)  # NC-YYYY-XXX

    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    source = Column(Enum(NCSource), nullable=False)
    severity = Column(Enum(NCSeverity), nullable=False)
    status = Column(Enum(NCStatus), default=NCStatus.OPEN, nullable=False)

    # Detection Details
    detected_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    detected_by = Column(String(100), nullable=False)
    department = Column(String(100))
    location = Column(String(200))

    # Related References
    related_document = Column(String(100))  # QSF reference, etc.
    related_equipment = Column(String(100))
    related_test_request = Column(String(50))
    related_batch = Column(String(50))

    # Impact Assessment
    impact_description = Column(Text)
    quantity_affected = Column(Integer)
    cost_impact = Column(Numeric(10, 2))

    # Containment Actions
    immediate_action = Column(Text)
    containment_date = Column(DateTime)
    containment_by = Column(String(100))

    # Assignment
    assigned_to = Column(String(100))
    assigned_date = Column(DateTime)
    target_closure_date = Column(Date)
    actual_closure_date = Column(Date)

    # Verification
    verified_by = Column(String(100))
    verification_date = Column(DateTime)
    verification_comments = Column(Text)
    effectiveness_verified = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(100), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(100))

    # Relationships
    root_cause_analyses = relationship("RootCauseAnalysis", back_populates="nonconformance", cascade="all, delete-orphan")
    capa_actions = relationship("CAPAAction", back_populates="nonconformance", cascade="all, delete-orphan")


class RootCauseAnalysis(Base):
    """Root Cause Analysis table."""

    __tablename__ = "root_cause_analysis"

    id = Column(Integer, primary_key=True, index=True)
    nc_id = Column(Integer, ForeignKey("nonconformances.id"), nullable=False)

    # RCA Details
    method = Column(Enum(RCAMethod), nullable=False)
    analysis_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    analyzed_by = Column(String(100), nullable=False)

    # 5-Why Analysis
    five_why_data = Column(JSON)  # Stores array of why questions and answers
    # Example: [{"level": 1, "why": "Why did X happen?", "answer": "Because Y"}, ...]

    # Fishbone Analysis
    fishbone_data = Column(JSON)  # Stores fishbone categories and causes
    # Example: {"man": ["cause1", "cause2"], "machine": [...], "method": [...], "material": [...], "measurement": [...], "environment": [...]}

    # AI Suggestions
    ai_suggestions = Column(JSON)  # AI-generated root cause suggestions
    ai_model_used = Column(String(50))
    ai_confidence_score = Column(Numeric(3, 2))

    # Root Cause Conclusion
    root_cause = Column(Text, nullable=False)
    contributing_factors = Column(JSON)  # Array of contributing factors

    # Evidence
    evidence_attachments = Column(JSON)  # Array of file paths/URLs
    supporting_data = Column(Text)

    # Approval
    approved_by = Column(String(100))
    approval_date = Column(DateTime)
    approval_comments = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    nonconformance = relationship("NonConformance", back_populates="root_cause_analyses")


class CAPAAction(Base):
    """CAPA Actions table."""

    __tablename__ = "capa_actions"

    id = Column(Integer, primary_key=True, index=True)
    capa_number = Column(String(50), unique=True, nullable=False, index=True)  # CAPA-YYYY-XXX
    nc_id = Column(Integer, ForeignKey("nonconformances.id"), nullable=False)

    # CAPA Details
    capa_type = Column(Enum(CAPAType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(CAPAStatus), default=CAPAStatus.PENDING, nullable=False)

    # Assignment
    assigned_to = Column(String(100), nullable=False)
    assigned_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    assigned_by = Column(String(100), nullable=False)

    # Timeline
    due_date = Column(Date, nullable=False)
    completed_date = Column(Date)

    # Implementation
    implementation_plan = Column(Text)
    resources_required = Column(JSON)  # Array of resources needed
    estimated_cost = Column(Numeric(10, 2))
    actual_cost = Column(Numeric(10, 2))

    # Execution
    action_taken = Column(Text)
    completion_evidence = Column(JSON)  # Array of file paths/URLs
    completion_comments = Column(Text)

    # Effectiveness Verification
    verification_method = Column(Text)
    verification_criteria = Column(Text)
    verification_due_date = Column(Date)
    verification_date = Column(Date)
    verified_by = Column(String(100))
    verification_result = Column(Boolean)
    verification_comments = Column(Text)
    effectiveness_rating = Column(Integer)  # 1-5 scale

    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    follow_up_comments = Column(Text)

    # Closure
    closed_by = Column(String(100))
    closure_date = Column(DateTime)
    closure_comments = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(100), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(100))

    # Relationships
    nonconformance = relationship("NonConformance", back_populates="capa_actions")
