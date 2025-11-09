"""
SQLAlchemy ORM Models for Audit & Risk Management System
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Boolean,
    ForeignKey, CheckConstraint, Index, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()


class AuditProgram(Base):
    """Annual Audit Program (QSF1701)"""
    __tablename__ = "audit_program"

    id = Column(Integer, primary_key=True, index=True)
    program_year = Column(Integer, nullable=False)
    program_number = Column(String(50), unique=True, nullable=False)
    program_title = Column(String(255), nullable=False)
    scope = Column(Text)
    objectives = Column(Text)
    prepared_by = Column(String(100))
    reviewed_by = Column(String(100))
    approved_by = Column(String(100))
    status = Column(String(50), default="DRAFT")
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    schedules = relationship("AuditSchedule", back_populates="program", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("program_year >= 2024", name="chk_program_year"),
        Index("idx_audit_program_year", "program_year"),
        Index("idx_audit_program_status", "status"),
    )


class AuditSchedule(Base):
    """Audit Schedule"""
    __tablename__ = "audit_schedule"

    id = Column(Integer, primary_key=True, index=True)
    audit_number = Column(String(50), unique=True, nullable=False)
    program_id = Column(Integer, ForeignKey("audit_program.id", ondelete="CASCADE"))
    audit_type = Column(String(50), nullable=False)
    audit_scope = Column(String(100), nullable=False)
    department = Column(String(100))
    process_area = Column(String(100))
    standard_reference = Column(String(100))
    planned_date = Column(Date, nullable=False)
    actual_date = Column(Date)
    duration_days = Column(Integer)
    lead_auditor = Column(String(100))
    audit_team = Column(Text)
    auditee = Column(String(100))
    status = Column(String(50), default="SCHEDULED")
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    program = relationship("AuditProgram", back_populates="schedules")
    findings = relationship("AuditFinding", back_populates="audit", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_audit_schedule_number", "audit_number"),
        Index("idx_audit_schedule_program", "program_id"),
        Index("idx_audit_schedule_status", "status"),
        Index("idx_audit_schedule_date", "planned_date"),
    )


class AuditFinding(Base):
    """Audit Findings with NC linkage"""
    __tablename__ = "audit_findings"

    id = Column(Integer, primary_key=True, index=True)
    finding_number = Column(String(50), unique=True, nullable=False)
    audit_id = Column(Integer, ForeignKey("audit_schedule.id", ondelete="CASCADE"))
    finding_type = Column(String(50), nullable=False)
    severity = Column(String(50))
    category = Column(String(100))
    clause_reference = Column(String(100))
    area_audited = Column(String(100))
    description = Column(Text, nullable=False)
    objective_evidence = Column(Text)
    requirement = Column(Text)
    root_cause = Column(Text)
    corrective_action = Column(Text)
    responsible_person = Column(String(100))
    target_date = Column(Date)
    actual_closure_date = Column(Date)
    status = Column(String(50), default="OPEN")
    nc_reference = Column(String(50))
    effectiveness_verified = Column(Boolean, default=False)
    verified_by = Column(String(100))
    verified_date = Column(Date)
    attachments = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    audit = relationship("AuditSchedule", back_populates="findings")

    __table_args__ = (
        Index("idx_audit_findings_number", "finding_number"),
        Index("idx_audit_findings_audit", "audit_id"),
        Index("idx_audit_findings_type", "finding_type"),
        Index("idx_audit_findings_status", "status"),
        Index("idx_audit_findings_nc", "nc_reference"),
    )


class RiskRegister(Base):
    """Risk Register with 5x5 Matrix"""
    __tablename__ = "risk_register"

    id = Column(Integer, primary_key=True, index=True)
    risk_number = Column(String(50), unique=True, nullable=False)
    risk_category = Column(String(100), nullable=False)
    process_area = Column(String(100))
    department = Column(String(100))
    risk_description = Column(Text, nullable=False)
    risk_source = Column(String(255))
    consequences = Column(Text)
    existing_controls = Column(Text)

    # Inherent Risk
    inherent_likelihood = Column(Integer)
    inherent_impact = Column(Integer)

    # Residual Risk
    residual_likelihood = Column(Integer)
    residual_impact = Column(Integer)

    risk_treatment = Column(String(50))
    treatment_plan = Column(Text)
    risk_owner = Column(String(100))
    target_date = Column(Date)
    review_frequency = Column(String(50))
    last_review_date = Column(Date)
    next_review_date = Column(Date)
    status = Column(String(50), default="ACTIVE")
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    review_history = relationship("RiskReviewHistory", back_populates="risk", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("inherent_likelihood BETWEEN 1 AND 5", name="chk_inherent_likelihood"),
        CheckConstraint("inherent_impact BETWEEN 1 AND 5", name="chk_inherent_impact"),
        CheckConstraint("residual_likelihood BETWEEN 1 AND 5", name="chk_residual_likelihood"),
        CheckConstraint("residual_impact BETWEEN 1 AND 5", name="chk_residual_impact"),
        Index("idx_risk_register_number", "risk_number"),
        Index("idx_risk_register_category", "risk_category"),
        Index("idx_risk_register_owner", "risk_owner"),
        Index("idx_risk_register_status", "status"),
    )

    @property
    def inherent_risk_score(self):
        if self.inherent_likelihood and self.inherent_impact:
            return self.inherent_likelihood * self.inherent_impact
        return 0

    @property
    def inherent_risk_level(self):
        score = self.inherent_risk_score
        if score <= 4:
            return "LOW"
        elif score <= 12:
            return "MEDIUM"
        elif score <= 16:
            return "HIGH"
        else:
            return "CRITICAL"

    @property
    def residual_risk_score(self):
        if self.residual_likelihood and self.residual_impact:
            return self.residual_likelihood * self.residual_impact
        return 0

    @property
    def residual_risk_level(self):
        score = self.residual_risk_score
        if score <= 4:
            return "LOW"
        elif score <= 12:
            return "MEDIUM"
        elif score <= 16:
            return "HIGH"
        else:
            return "CRITICAL"


class RiskReviewHistory(Base):
    """Risk Review History"""
    __tablename__ = "risk_review_history"

    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risk_register.id", ondelete="CASCADE"))
    review_date = Column(Date, nullable=False)
    reviewed_by = Column(String(100))
    likelihood_before = Column(Integer)
    impact_before = Column(Integer)
    likelihood_after = Column(Integer)
    impact_after = Column(Integer)
    changes_made = Column(Text)
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    risk = relationship("RiskRegister", back_populates="review_history")

    __table_args__ = (
        Index("idx_risk_review_risk_id", "risk_id"),
    )


class ComplianceTracking(Base):
    """Compliance Tracking"""
    __tablename__ = "compliance_tracking"

    id = Column(Integer, primary_key=True, index=True)
    standard_name = Column(String(100), nullable=False)
    clause_number = Column(String(50), nullable=False)
    clause_title = Column(String(255))
    requirement = Column(Text)
    compliance_status = Column(String(50), default="COMPLIANT")
    evidence_reference = Column(Text)
    last_audit_date = Column(Date)
    next_audit_date = Column(Date)
    responsible_person = Column(String(100))
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_compliance_standard", "standard_name"),
        Index("idx_compliance_status", "compliance_status"),
    )
