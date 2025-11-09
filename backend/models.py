"""
Database Models for LIMS-QMS Platform
Includes all tables from Sessions 2-8
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Float, Boolean,
    ForeignKey, Enum, JSON, DECIMAL
)
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base
import enum


# ============================================================================
# SESSION 2: Document Management System
# ============================================================================

class DocumentType(str, enum.Enum):
    QSF = "QSF"  # Quality System Form
    QSP = "QSP"  # Quality System Procedure
    QSM = "QSM"  # Quality System Manual
    WI = "WI"    # Work Instruction
    TR = "TR"    # Technical Report


class DocumentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    OBSOLETE = "OBSOLETE"


class QMSDocument(Base):
    __tablename__ = "qms_documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)
    revision = Column(String(20), default="1.0")
    owner = Column(String(100), nullable=False)
    status = Column(String(20), default="DRAFT")
    effective_date = Column(Date)
    review_date = Column(Date)
    file_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    revisions = relationship("DocumentRevision", back_populates="document")
    distributions = relationship("DocumentDistribution", back_populates="document")


class DocumentRevision(Base):
    __tablename__ = "document_revisions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("qms_documents.id"), nullable=False)
    revision = Column(String(20), nullable=False)
    description = Column(Text)
    revised_by = Column(String(100), nullable=False)
    reviewed_by = Column(String(100))
    approved_by = Column(String(100))
    revision_date = Column(DateTime, default=datetime.utcnow)

    document = relationship("QMSDocument", back_populates="revisions")


class DocumentDistribution(Base):
    __tablename__ = "document_distribution"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("qms_documents.id"), nullable=False)
    copy_number = Column(String(20), nullable=False)
    holder_name = Column(String(100), nullable=False)
    holder_department = Column(String(100))
    issued_date = Column(Date, nullable=False)
    is_controlled = Column(Boolean, default=True)

    document = relationship("QMSDocument", back_populates="distributions")


# ============================================================================
# SESSION 3: Equipment Calibration & Maintenance
# ============================================================================

class EquipmentMaster(Base):
    __tablename__ = "equipment_master"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    manufacturer = Column(String(200))
    model = Column(String(100))
    serial_number = Column(String(100))
    location = Column(String(200))
    category = Column(String(100))
    calibration_frequency_days = Column(Integer)
    next_calibration_date = Column(Date)
    status = Column(String(50), default="Active")
    purchase_date = Column(Date)
    purchase_cost = Column(DECIMAL(10, 2))
    qr_code_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    calibrations = relationship("CalibrationRecord", back_populates="equipment")
    maintenance = relationship("PreventiveMaintenanceSchedule", back_populates="equipment")


class CalibrationRecord(Base):
    __tablename__ = "calibration_records"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id"), nullable=False)
    calibration_date = Column(Date, nullable=False)
    next_due_date = Column(Date, nullable=False)
    calibrated_by = Column(String(100), nullable=False)
    calibration_agency = Column(String(200))
    certificate_number = Column(String(100))
    result = Column(String(50))  # Pass/Fail
    remarks = Column(Text)
    certificate_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("EquipmentMaster", back_populates="calibrations")


class PreventiveMaintenanceSchedule(Base):
    __tablename__ = "preventive_maintenance_schedule"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id"), nullable=False)
    maintenance_type = Column(String(100), nullable=False)
    frequency_days = Column(Integer, nullable=False)
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date, nullable=False)
    performed_by = Column(String(100))
    status = Column(String(50), default="Scheduled")
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("EquipmentMaster", back_populates="maintenance")


# ============================================================================
# SESSION 4: Training & Competency
# ============================================================================

class TrainingMaster(Base):
    __tablename__ = "training_master"

    id = Column(Integer, primary_key=True, index=True)
    training_code = Column(String(50), unique=True, nullable=False, index=True)
    training_name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # Technical, Safety, QMS, etc.
    duration_hours = Column(Float)
    validity_months = Column(Integer)
    trainer = Column(String(100))
    department = Column(String(100))
    is_mandatory = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    attendance = relationship("TrainingAttendance", back_populates="training")


class EmployeeTrainingMatrix(Base):
    __tablename__ = "employee_training_matrix"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False, index=True)
    employee_name = Column(String(100), nullable=False)
    department = Column(String(100))
    designation = Column(String(100))
    email = Column(String(100))
    joining_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)


class TrainingAttendance(Base):
    __tablename__ = "training_attendance"

    id = Column(Integer, primary_key=True, index=True)
    training_id = Column(Integer, ForeignKey("training_master.id"), nullable=False)
    employee_id = Column(String(50), nullable=False)
    training_date = Column(Date, nullable=False)
    completion_date = Column(Date)
    score = Column(Float)
    status = Column(String(50))  # Completed, In Progress, Failed
    certificate_number = Column(String(100))
    expiry_date = Column(Date)
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    training = relationship("TrainingMaster", back_populates="attendance")


# ============================================================================
# SESSION 5: LIMS Core - Test Request & Sample Management
# ============================================================================

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    customer_type = Column(String(50))  # Manufacturer, Trader, etc.
    credit_limit = Column(DECIMAL(12, 2))
    payment_terms = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    test_requests = relationship("TestRequest", back_populates="customer")


class TestRequest(Base):
    __tablename__ = "test_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    request_date = Column(Date, nullable=False)
    required_date = Column(Date)
    sample_description = Column(Text)
    test_type = Column(String(100))  # IEC 61215, IEC 61730, etc.
    priority = Column(String(20), default="Normal")
    status = Column(String(50), default="Received")
    assigned_to = Column(String(100))
    quote_amount = Column(DECIMAL(12, 2))
    quote_approved = Column(Boolean, default=False)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="test_requests")
    samples = relationship("Sample", back_populates="test_request")


class Sample(Base):
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(String(50), unique=True, nullable=False, index=True)
    test_request_id = Column(Integer, ForeignKey("test_requests.id"), nullable=False)
    sample_name = Column(String(200), nullable=False)
    sample_type = Column(String(100))
    manufacturer = Column(String(200))
    model = Column(String(100))
    serial_number = Column(String(100))
    received_date = Column(Date, nullable=False)
    condition_on_receipt = Column(Text)
    storage_location = Column(String(200))
    barcode = Column(String(100))
    status = Column(String(50), default="Received")
    disposal_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    test_request = relationship("TestRequest", back_populates="samples")
    test_parameters = relationship("TestParameter", back_populates="sample")


class TestParameter(Base):
    __tablename__ = "test_parameters"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)
    parameter_name = Column(String(200), nullable=False)
    test_method = Column(String(200))
    specification = Column(String(200))
    result = Column(String(200))
    unit = Column(String(50))
    pass_fail = Column(String(20))
    tested_by = Column(String(100))
    tested_date = Column(Date)
    reviewed_by = Column(String(100))
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    sample = relationship("Sample", back_populates="test_parameters")


# ============================================================================
# SESSION 6: IEC Test Report Generation
# ============================================================================

class IECTestExecution(Base):
    __tablename__ = "iec_test_execution"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String(50), unique=True, nullable=False, index=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)
    standard = Column(String(50), nullable=False)  # IEC 61215, 61730, 61701
    test_name = Column(String(200), nullable=False)
    test_date = Column(Date, nullable=False)
    operator = Column(String(100))
    equipment_used = Column(String(200))
    test_data = Column(JSON)  # Store test measurements as JSON
    pass_fail_criteria = Column(Text)
    result = Column(String(20))  # Pass/Fail
    graphs_generated = Column(Boolean, default=False)
    graph_paths = Column(JSON)  # Array of graph file paths
    created_at = Column(DateTime, default=datetime.utcnow)


class IECTestReport(Base):
    __tablename__ = "iec_test_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_number = Column(String(50), unique=True, nullable=False, index=True)
    test_execution_id = Column(Integer, ForeignKey("iec_test_execution.id"), nullable=False)
    report_date = Column(Date, nullable=False)
    generated_by = Column(String(100))
    reviewed_by = Column(String(100))
    approved_by = Column(String(100))
    report_path = Column(String(500))
    certificate_path = Column(String(500))
    qr_code_path = Column(String(500))
    digital_signature = Column(Text)
    status = Column(String(50), default="Draft")
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# SESSION 7: Non-Conformance & CAPA
# ============================================================================

class NonConformance(Base):
    __tablename__ = "nonconformances"

    id = Column(Integer, primary_key=True, index=True)
    nc_number = Column(String(50), unique=True, nullable=False, index=True)
    nc_date = Column(Date, nullable=False)
    source = Column(String(100))  # Internal Audit, Customer Complaint, etc.
    category = Column(String(100))  # Quality, Process, Documentation, etc.
    description = Column(Text, nullable=False)
    detected_by = Column(String(100))
    department = Column(String(100))
    severity = Column(String(20))  # Critical, Major, Minor
    status = Column(String(50), default="Open")
    closure_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    root_cause = relationship("RootCauseAnalysis", back_populates="nonconformance", uselist=False)
    capa_actions = relationship("CAPAAction", back_populates="nonconformance")


class RootCauseAnalysis(Base):
    __tablename__ = "root_cause_analysis"

    id = Column(Integer, primary_key=True, index=True)
    nc_id = Column(Integer, ForeignKey("nonconformances.id"), nullable=False)
    analysis_method = Column(String(50))  # 5-Why, Fishbone, etc.
    analysis_data = Column(JSON)  # Store 5-Why or Fishbone data as JSON
    root_cause = Column(Text)
    ai_suggestions = Column(JSON)  # AI-generated root cause suggestions
    analyzed_by = Column(String(100))
    analysis_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    nonconformance = relationship("NonConformance", back_populates="root_cause")


class CAPAAction(Base):
    __tablename__ = "capa_actions"

    id = Column(Integer, primary_key=True, index=True)
    capa_number = Column(String(50), unique=True, nullable=False, index=True)
    nc_id = Column(Integer, ForeignKey("nonconformances.id"), nullable=False)
    action_type = Column(String(50))  # Corrective, Preventive
    description = Column(Text, nullable=False)
    responsible_person = Column(String(100))
    target_date = Column(Date, nullable=False)
    completion_date = Column(Date)
    status = Column(String(50), default="Planned")
    effectiveness_verified = Column(Boolean, default=False)
    verification_date = Column(Date)
    verified_by = Column(String(100))
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    nonconformance = relationship("NonConformance", back_populates="capa_actions")


# ============================================================================
# SESSION 8: Audit & Risk Management
# ============================================================================

class AuditProgram(Base):
    __tablename__ = "audit_program"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(String(50), unique=True, nullable=False, index=True)
    year = Column(Integer, nullable=False)
    program_name = Column(String(200), nullable=False)
    scope = Column(Text)
    objectives = Column(Text)
    prepared_by = Column(String(100))
    approved_by = Column(String(100))
    approval_date = Column(Date)
    status = Column(String(50), default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)

    schedules = relationship("AuditSchedule", back_populates="program")


class AuditSchedule(Base):
    __tablename__ = "audit_schedule"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("audit_program.id"), nullable=False)
    audit_type = Column(String(100))  # Internal, External, Surveillance
    audit_area = Column(String(200), nullable=False)
    planned_date = Column(Date, nullable=False)
    actual_date = Column(Date)
    lead_auditor = Column(String(100))
    audit_team = Column(String(500))
    status = Column(String(50), default="Scheduled")
    report_reference = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    program = relationship("AuditProgram", back_populates="schedules")
    findings = relationship("AuditFinding", back_populates="audit")


class AuditFinding(Base):
    __tablename__ = "audit_findings"

    id = Column(Integer, primary_key=True, index=True)
    finding_number = Column(String(50), unique=True, nullable=False, index=True)
    audit_id = Column(Integer, ForeignKey("audit_schedule.id"), nullable=False)
    finding_type = Column(String(50))  # Observation, Minor NC, Major NC
    clause_reference = Column(String(100))
    description = Column(Text, nullable=False)
    evidence = Column(Text)
    raised_by = Column(String(100))
    finding_date = Column(Date, nullable=False)
    nc_id = Column(Integer, ForeignKey("nonconformances.id"))  # Link to NC if created
    status = Column(String(50), default="Open")
    closure_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    audit = relationship("AuditSchedule", back_populates="findings")


class RiskRegister(Base):
    __tablename__ = "risk_register"

    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(String(50), unique=True, nullable=False, index=True)
    risk_category = Column(String(100))  # Operational, Financial, Compliance, etc.
    risk_description = Column(Text, nullable=False)
    process_area = Column(String(200))
    likelihood = Column(Integer)  # 1-5 scale
    impact = Column(Integer)  # 1-5 scale
    risk_score = Column(Integer)  # likelihood * impact
    risk_level = Column(String(20))  # Low, Medium, High, Critical
    mitigation_plan = Column(Text)
    owner = Column(String(100))
    status = Column(String(50), default="Active")
    review_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# SESSION 9: Analytics & Customer Portal (New Tables)
# ============================================================================

class CustomerPortalUser(Base):
    __tablename__ = "customer_portal_users"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200))
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalyticsKPI(Base):
    __tablename__ = "analytics_kpis"

    id = Column(Integer, primary_key=True, index=True)
    kpi_name = Column(String(200), nullable=False)
    kpi_category = Column(String(100))  # Executive, Operational, Quality
    kpi_value = Column(Float)
    target_value = Column(Float)
    unit = Column(String(50))
    period = Column(String(50))  # Daily, Weekly, Monthly, Quarterly, Yearly
    period_date = Column(Date, nullable=False)
    department = Column(String(100))
    calculated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        # Ensure unique KPI per period
        # UniqueConstraint('kpi_name', 'period_date', name='uix_kpi_period'),
    )
