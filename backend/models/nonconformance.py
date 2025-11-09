"""
Non-Conformance & CAPA Models (Session 7)
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from backend.core.database import Base


class NCStatus(str, enum.Enum):
    OPEN = "open"
    UNDER_INVESTIGATION = "under_investigation"
    CAPA_IN_PROGRESS = "capa_in_progress"
    VERIFICATION_PENDING = "verification_pending"
    CLOSED = "closed"


class NCCategory(str, enum.Enum):
    TESTING = "testing"
    CALIBRATION = "calibration"
    DOCUMENTATION = "documentation"
    PROCESS = "process"
    CUSTOMER_COMPLAINT = "customer_complaint"


class NonConformance(Base):
    """Non-conformance records"""
    __tablename__ = "nonconformances"

    id = Column(Integer, primary_key=True, index=True)
    nc_number = Column(String(50), unique=True, nullable=False, index=True)  # NC-YYYY-XXX
    nc_category = Column(SQLEnum(NCCategory), nullable=False)
    detected_date = Column(Date, nullable=False)
    detected_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=False)
    immediate_action = Column(Text)
    severity = Column(String(50))  # critical, major, minor
    status = Column(SQLEnum(NCStatus), default=NCStatus.OPEN)
    related_module = Column(String(50))  # lims, equipment, training, etc.
    related_entity_id = Column(Integer)
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    target_closure_date = Column(Date)
    actual_closure_date = Column(Date)
    ai_suggested_root_cause = Column(Text)  # AI-generated suggestion
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    root_cause_analysis = relationship("RootCauseAnalysis", back_populates="nonconformance", uselist=False)
    capa_actions = relationship("CAPAAction", back_populates="nonconformance")


class RootCauseAnalysis(Base):
    """Root cause analysis (5-Why, Fishbone)"""
    __tablename__ = "root_cause_analysis"

    id = Column(Integer, primary_key=True, index=True)
    nc_id = Column(Integer, ForeignKey("nonconformances.id"), unique=True, nullable=False)
    analysis_method = Column(String(50))  # 5-why, fishbone, other
    why_1 = Column(Text)
    why_2 = Column(Text)
    why_3 = Column(Text)
    why_4 = Column(Text)
    why_5 = Column(Text)
    root_cause = Column(Text, nullable=False)
    contributing_factors = Column(Text)  # JSON array
    analysis_date = Column(Date, nullable=False)
    analyzed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    nonconformance = relationship("NonConformance", back_populates="root_cause_analysis")


class CAPAAction(Base):
    """Corrective and Preventive Actions"""
    __tablename__ = "capa_actions"

    id = Column(Integer, primary_key=True, index=True)
    capa_number = Column(String(50), unique=True, nullable=False, index=True)
    nc_id = Column(Integer, ForeignKey("nonconformances.id"), nullable=False)
    action_type = Column(String(50), nullable=False)  # corrective, preventive
    action_description = Column(Text, nullable=False)
    responsible_person_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_date = Column(Date, nullable=False)
    completion_date = Column(Date)
    status = Column(String(50))  # planned, in_progress, completed, verified
    effectiveness_check = Column(Text)
    effectiveness_result = Column(String(50))  # effective, not_effective
    verified_by_id = Column(Integer, ForeignKey("users.id"))
    verification_date = Column(Date)
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    nonconformance = relationship("NonConformance", back_populates="capa_actions")
