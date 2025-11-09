"""
Audit & Risk Management Models (Session 8)
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.core.database import Base


class AuditProgram(Base):
    """Annual audit program (QSF1701)"""
    __tablename__ = "audit_program"

    id = Column(Integer, primary_key=True, index=True)
    program_year = Column(Integer, nullable=False, unique=True, index=True)
    program_objectives = Column(Text)
    scope = Column(Text)
    audit_criteria = Column(Text)  # ISO 17025:2017, ISO 9001:2015
    approved_by_id = Column(Integer, ForeignKey("users.id"))
    approval_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    audit_schedules = relationship("AuditSchedule", back_populates="program")


class AuditSchedule(Base):
    """Audit scheduling"""
    __tablename__ = "audit_schedule"

    id = Column(Integer, primary_key=True, index=True)
    audit_program_id = Column(Integer, ForeignKey("audit_program.id"), nullable=False)
    audit_number = Column(String(50), unique=True, nullable=False, index=True)
    audit_type = Column(String(50), nullable=False)  # internal, external, surveillance
    audit_area = Column(String(100), nullable=False)  # Department/Process
    planned_date = Column(Date, nullable=False, index=True)
    actual_date = Column(Date)
    lead_auditor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    audit_team = Column(Text)  # JSON array of auditor IDs
    status = Column(String(50))  # planned, in_progress, completed
    audit_report_path = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    program = relationship("AuditProgram", back_populates="audit_schedules")
    findings = relationship("AuditFinding", back_populates="audit")


class AuditFinding(Base):
    """Audit findings"""
    __tablename__ = "audit_findings"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audit_schedule.id"), nullable=False)
    finding_number = Column(String(50), unique=True, nullable=False, index=True)
    finding_type = Column(String(50), nullable=False)  # major_nc, minor_nc, observation, opportunity
    clause_reference = Column(String(100))  # ISO clause number
    description = Column(Text, nullable=False)
    evidence = Column(Text)
    recommendation = Column(Text)
    nc_id = Column(Integer, ForeignKey("nonconformances.id"))  # Link to NC if generated
    status = Column(String(50))  # open, closed
    closure_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    audit = relationship("AuditSchedule", back_populates="findings")


class RiskRegister(Base):
    """Risk register (5x5 matrix)"""
    __tablename__ = "risk_register"

    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(String(50), unique=True, nullable=False, index=True)
    risk_category = Column(String(100))  # operational, quality, compliance, financial
    risk_description = Column(Text, nullable=False)
    process_area = Column(String(100))
    likelihood = Column(Integer, nullable=False)  # 1-5
    consequence = Column(Integer, nullable=False)  # 1-5
    risk_score = Column(Integer)  # likelihood * consequence
    risk_level = Column(String(50))  # low, medium, high, critical
    mitigation_plan = Column(Text)
    control_measures = Column(Text)
    responsible_person_id = Column(Integer, ForeignKey("users.id"))
    review_date = Column(Date)
    status = Column(String(50))  # active, mitigated, closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
