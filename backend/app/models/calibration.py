"""
Calibration models for calibration management
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey, Boolean,
    Numeric, Date, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base
from app.models.base import User, WorkflowStatus
import enum


class CalibrationType(str, enum.Enum):
    """Calibration type"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    IN_HOUSE = "in_house"


class CalibrationResult(str, enum.Enum):
    """Calibration result status"""
    PASS = "pass"
    FAIL = "fail"
    LIMITED_USE = "limited_use"
    OUT_OF_TOLERANCE = "out_of_tolerance"


class CalibrationMaster(Base):
    """Calibration master data - vendor and standards information"""
    __tablename__ = "calibration_master"

    id = Column(Integer, primary_key=True, index=True)

    # Vendor Information
    vendor_name = Column(String(255), nullable=False, unique=True, index=True)
    vendor_code = Column(String(50), unique=True)
    vendor_contact_person = Column(String(100))
    vendor_email = Column(String(100))
    vendor_phone = Column(String(20))
    vendor_address = Column(Text)

    # Accreditation
    accreditation_body = Column(String(100))  # NABL, ISO 17025, etc.
    accreditation_number = Column(String(100))
    accreditation_valid_until = Column(Date)
    scope_of_accreditation = Column(Text)

    # Performance metrics
    total_calibrations = Column(Integer, default=0)
    on_time_delivery_count = Column(Integer, default=0)
    delayed_delivery_count = Column(Integer, default=0)
    average_turnaround_days = Column(Numeric(5, 2))
    quality_rating = Column(Numeric(3, 2))  # Out of 5.0

    # Flags
    is_approved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    created_by = relationship("User")
    calibration_records = relationship("CalibrationRecord", back_populates="vendor")


class CalibrationRecord(Base):
    """Calibration records for equipment"""
    __tablename__ = "calibration_records"

    id = Column(Integer, primary_key=True, index=True)

    # Unique calibration ID
    calibration_id = Column(String(50), unique=True, nullable=False, index=True)

    # Link to equipment
    equipment_id = Column(Integer, ForeignKey("equipment_master.id"), nullable=False, index=True)

    # Calibration details
    calibration_type = Column(SQLEnum(CalibrationType), nullable=False)
    calibration_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    next_calibration_date = Column(Date, index=True)

    # Vendor information (for external calibrations)
    vendor_id = Column(Integer, ForeignKey("calibration_master.id"))

    # Certificate details
    certificate_number = Column(String(100), unique=True, index=True)
    certificate_issue_date = Column(Date)
    certificate_file_path = Column(String(500))
    certificate_data = Column(JSON)  # OCR extracted data

    # Calibration result
    result = Column(SQLEnum(CalibrationResult), nullable=False)
    result_details = Column(Text)

    # Measurement data
    as_found_data = Column(JSON)  # Before calibration measurements
    as_left_data = Column(JSON)  # After calibration measurements
    uncertainty = Column(String(100))
    environmental_conditions = Column(JSON)  # Temp, humidity, etc.

    # Standards used
    reference_standards = Column(JSON)  # Array of standard equipment used
    traceability_chain = Column(Text)

    # Cost tracking
    calibration_cost = Column(Numeric(15, 2))
    additional_charges = Column(Numeric(15, 2))
    total_cost = Column(Numeric(15, 2))

    # Timeline tracking
    scheduled_date = Column(Date)
    sent_to_vendor_date = Column(Date)
    received_from_vendor_date = Column(Date)
    actual_calibration_date = Column(Date)
    turnaround_days = Column(Integer)

    # Workflow status
    workflow_status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    workflow_id = Column(Integer, ForeignKey("workflow_records.id"))

    # People involved
    performed_by_id = Column(Integer, ForeignKey("users.id"))
    verified_by_id = Column(Integer, ForeignKey("users.id"))
    approved_by_id = Column(Integer, ForeignKey("users.id"))

    # Action taken
    action_taken = Column(Text)
    corrective_action = Column(Text)
    remarks = Column(Text)

    # Flags
    is_alert_sent = Column(Boolean, default=False)
    alert_30_days = Column(Boolean, default=False)
    alert_15_days = Column(Boolean, default=False)
    alert_7_days = Column(Boolean, default=False)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    equipment = relationship("EquipmentMaster", back_populates="calibration_records")
    vendor = relationship("CalibrationMaster", back_populates="calibration_records")
    workflow = relationship("WorkflowRecord")
    performed_by = relationship("User", foreign_keys=[performed_by_id])
    verified_by = relationship("User", foreign_keys=[verified_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    created_by = relationship("User", foreign_keys=[created_by_id])


class CalibrationSchedule(Base):
    """Automatic calibration scheduling based on equipment calibration frequency"""
    __tablename__ = "calibration_schedule"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id"), nullable=False, index=True)

    # Schedule details
    scheduled_date = Column(Date, nullable=False, index=True)
    calibration_type = Column(SQLEnum(CalibrationType))
    preferred_vendor_id = Column(Integer, ForeignKey("calibration_master.id"))

    # Status
    is_completed = Column(Boolean, default=False)
    completed_calibration_id = Column(Integer, ForeignKey("calibration_records.id"))
    is_overdue = Column(Boolean, default=False)

    # Alerts
    alert_30_days_sent = Column(Boolean, default=False)
    alert_15_days_sent = Column(Boolean, default=False)
    alert_7_days_sent = Column(Boolean, default=False)
    alert_overdue_sent = Column(Boolean, default=False)

    # Notes
    notes = Column(Text)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    equipment = relationship("EquipmentMaster")
    preferred_vendor = relationship("CalibrationMaster")
    completed_calibration = relationship("CalibrationRecord")
