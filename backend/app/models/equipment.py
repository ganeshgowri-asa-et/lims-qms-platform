"""Equipment Calibration & Maintenance models."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class EquipmentStatus(str, enum.Enum):
    """Equipment status enumeration."""
    OPERATIONAL = "operational"
    UNDER_CALIBRATION = "under_calibration"
    UNDER_MAINTENANCE = "under_maintenance"
    OUT_OF_SERVICE = "out_of_service"
    RETIRED = "retired"


class CalibrationStatus(str, enum.Enum):
    """Calibration status enumeration."""
    DUE = "due"
    OVERDUE = "overdue"
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"


class MaintenanceType(str, enum.Enum):
    """Maintenance type enumeration."""
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    BREAKDOWN = "breakdown"
    CALIBRATION = "calibration"


class EquipmentMaster(Base):
    """Equipment master data table."""
    __tablename__ = "equipment_master"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String(50), unique=True, nullable=False, index=True)

    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    manufacturer = Column(String(100))
    model_number = Column(String(100))
    serial_number = Column(String(100), unique=True)

    # Classification
    category = Column(String(100))
    equipment_type = Column(String(100))

    # Location and ownership
    location = Column(String(100))
    department = Column(String(100))
    responsible_person = Column(String(100))

    # Status
    status = Column(Enum(EquipmentStatus), default=EquipmentStatus.OPERATIONAL, nullable=False)

    # Acquisition details
    purchase_date = Column(DateTime)
    purchase_cost = Column(Float)
    supplier = Column(String(100))
    warranty_expiry = Column(DateTime)

    # Installation details
    installation_date = Column(DateTime)
    commissioned_date = Column(DateTime)

    # Calibration settings
    requires_calibration = Column(Boolean, default=True)
    calibration_frequency_days = Column(Integer, default=365)
    last_calibration_date = Column(DateTime)
    next_calibration_date = Column(DateTime)
    calibration_status = Column(Enum(CalibrationStatus))

    # Maintenance settings
    maintenance_frequency_days = Column(Integer, default=180)
    last_maintenance_date = Column(DateTime)
    next_maintenance_date = Column(DateTime)

    # OEE (Overall Equipment Effectiveness) tracking
    planned_uptime_hours = Column(Float, default=0)
    actual_uptime_hours = Column(Float, default=0)
    downtime_hours = Column(Float, default=0)
    availability_percentage = Column(Float, default=100.0)
    performance_percentage = Column(Float, default=100.0)
    quality_percentage = Column(Float, default=100.0)
    oee_percentage = Column(Float, default=100.0)

    # QR Code
    qr_code_path = Column(String(500))
    qr_code_generated_at = Column(DateTime)

    # Specifications
    technical_specs = Column(JSON)
    operating_range = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    retired_at = Column(DateTime)

    # Metadata
    metadata = Column(JSON)
    notes = Column(Text)

    # Relationships
    calibrations = relationship("CalibrationRecord", back_populates="equipment", cascade="all, delete-orphan")
    maintenance_schedules = relationship("PreventiveMaintenanceSchedule", back_populates="equipment", cascade="all, delete-orphan")


class CalibrationRecord(Base):
    """Calibration records table."""
    __tablename__ = "calibration_records"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id"), nullable=False)

    # Calibration details
    calibration_date = Column(DateTime, nullable=False)
    next_calibration_date = Column(DateTime, nullable=False)
    calibration_status = Column(Enum(CalibrationStatus), default=CalibrationStatus.IN_PROGRESS)

    # Performed by
    performed_by = Column(String(100), nullable=False)
    calibration_agency = Column(String(100))
    certificate_number = Column(String(100), unique=True)

    # Results
    result = Column(String(50))  # pass, fail, conditional
    accuracy_achieved = Column(Float)
    uncertainty = Column(Float)

    # Standards used
    reference_standard = Column(String(100))
    standard_certificate_number = Column(String(100))
    traceability = Column(String(255))

    # Measurements
    as_found_readings = Column(JSON)
    as_left_readings = Column(JSON)
    test_points = Column(JSON)

    # Environmental conditions
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)

    # Documentation
    certificate_path = Column(String(500))
    report_path = Column(String(500))

    # Review and approval
    reviewed_by = Column(String(100))
    approved_by = Column(String(100))
    reviewed_at = Column(DateTime)
    approved_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Metadata
    notes = Column(Text)
    metadata = Column(JSON)

    # Relationships
    equipment = relationship("EquipmentMaster", back_populates="calibrations")


class PreventiveMaintenanceSchedule(Base):
    """Preventive maintenance schedule and records."""
    __tablename__ = "preventive_maintenance_schedule"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id"), nullable=False)

    # Schedule details
    maintenance_type = Column(Enum(MaintenanceType), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    completed_date = Column(DateTime)

    # Status
    is_completed = Column(Boolean, default=False)
    is_overdue = Column(Boolean, default=False)

    # Performed by
    assigned_to = Column(String(100))
    performed_by = Column(String(100))

    # Maintenance details
    maintenance_description = Column(Text, nullable=False)
    checklist = Column(JSON)
    parts_replaced = Column(JSON)
    parts_cost = Column(Float)
    labor_hours = Column(Float)
    labor_cost = Column(Float)
    total_cost = Column(Float)

    # Results
    observations = Column(Text)
    issues_found = Column(Text)
    corrective_actions = Column(Text)

    # Documentation
    work_order_number = Column(String(50))
    report_path = Column(String(500))

    # Next maintenance
    next_maintenance_date = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Metadata
    notes = Column(Text)
    metadata = Column(JSON)

    # Relationships
    equipment = relationship("EquipmentMaster", back_populates="maintenance_schedules")
