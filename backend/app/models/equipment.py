"""
Equipment models for equipment management system
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey, Boolean,
    Numeric, Date, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base
from app.models.base import User
import enum


class EquipmentStatus(str, enum.Enum):
    """Equipment operational status"""
    OPERATIONAL = "operational"
    UNDER_CALIBRATION = "under_calibration"
    UNDER_MAINTENANCE = "under_maintenance"
    OUT_OF_ORDER = "out_of_order"
    RETIRED = "retired"
    QUARANTINED = "quarantined"


class EquipmentCategory(str, enum.Enum):
    """Equipment categories"""
    MEASURING_INSTRUMENT = "measuring_instrument"
    TESTING_EQUIPMENT = "testing_equipment"
    ANALYTICAL_INSTRUMENT = "analytical_instrument"
    ENVIRONMENTAL_CHAMBER = "environmental_chamber"
    SAFETY_EQUIPMENT = "safety_equipment"
    GENERAL_EQUIPMENT = "general_equipment"


class CalibrationFrequency(str, enum.Enum):
    """Calibration frequency options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"
    BIENNIAL = "biennial"
    AS_REQUIRED = "as_required"


class EquipmentMaster(Base):
    """Equipment master table - Main equipment registry"""
    __tablename__ = "equipment_master"

    id = Column(Integer, primary_key=True, index=True)

    # Unique Equipment ID (EQP-DEPT-YYYY-XXX)
    equipment_id = Column(String(50), unique=True, nullable=False, index=True)

    # Basic Information (from QSF0401)
    equipment_name = Column(String(255), nullable=False, index=True)
    equipment_code = Column(String(50), unique=True, index=True)
    category = Column(SQLEnum(EquipmentCategory), nullable=False)
    manufacturer = Column(String(255))
    model_number = Column(String(100))
    serial_number = Column(String(100), unique=True, index=True)

    # Department and Location
    department = Column(String(100), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    sub_location = Column(String(255))
    responsible_person_id = Column(Integer, ForeignKey("users.id"))

    # Procurement Details
    supplier_vendor = Column(String(255))
    purchase_order_number = Column(String(100))
    purchase_date = Column(Date)
    installation_date = Column(Date)
    warranty_expiry_date = Column(Date)
    asset_value = Column(Numeric(15, 2))

    # Technical Specifications
    technical_specifications = Column(JSON)  # Flexible JSON for various specs
    operating_range = Column(String(255))
    accuracy = Column(String(100))
    resolution = Column(String(100))

    # Calibration Information
    requires_calibration = Column(Boolean, default=True)
    calibration_frequency = Column(SQLEnum(CalibrationFrequency))
    last_calibration_date = Column(Date, index=True)
    next_calibration_date = Column(Date, index=True)
    calibration_standard_reference = Column(String(255))

    # Maintenance Information
    maintenance_frequency = Column(String(50))
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date, index=True)

    # Status and Usage
    status = Column(SQLEnum(EquipmentStatus), nullable=False, default=EquipmentStatus.OPERATIONAL)
    usage_hours = Column(Numeric(10, 2), default=0)
    max_usage_hours = Column(Numeric(10, 2))  # For lifecycle tracking

    # QR Code
    qr_code_data = Column(Text)  # Base64 encoded QR code image
    qr_code_url = Column(String(500))

    # Document References
    user_manual_url = Column(String(500))
    sop_reference = Column(String(100))  # Link to SOP document

    # Flags
    is_critical = Column(Boolean, default=False)  # Critical for operations
    is_active = Column(Boolean, default=True)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"))
    updated_by_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    responsible_person = relationship("User", foreign_keys=[responsible_person_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])
    specifications = relationship("EquipmentSpecification", back_populates="equipment", cascade="all, delete-orphan")
    calibration_records = relationship("CalibrationRecord", back_populates="equipment")
    maintenance_records = relationship("MaintenanceRecord", back_populates="equipment")
    history = relationship("EquipmentHistoryCard", back_populates="equipment", cascade="all, delete-orphan")
    utilization_records = relationship("EquipmentUtilization", back_populates="equipment")


class EquipmentSpecification(Base):
    """Detailed specifications for equipment ranges and accuracy"""
    __tablename__ = "equipment_specifications"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id"), nullable=False)

    # Specification details
    parameter_name = Column(String(100), nullable=False)
    measurement_range_min = Column(Numeric(15, 6))
    measurement_range_max = Column(Numeric(15, 6))
    unit = Column(String(50))
    accuracy = Column(String(100))
    resolution = Column(String(100))
    uncertainty = Column(String(100))

    # Additional details
    specification_notes = Column(Text)
    is_active = Column(Boolean, default=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    equipment = relationship("EquipmentMaster", back_populates="specifications")


class EquipmentHistoryCard(Base):
    """Complete history of all changes to equipment"""
    __tablename__ = "equipment_history_card"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id"), nullable=False, index=True)

    # Event details
    event_date = Column(DateTime(timezone=True), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # CALIBRATION, MAINTENANCE, REPAIR, STATUS_CHANGE, etc.
    description = Column(Text, nullable=False)

    # People involved
    performed_by_id = Column(Integer, ForeignKey("users.id"))
    verified_by_id = Column(Integer, ForeignKey("users.id"))

    # Details
    before_status = Column(String(50))
    after_status = Column(String(50))
    downtime_hours = Column(Numeric(10, 2))
    cost = Column(Numeric(15, 2))

    # Documents
    supporting_documents = Column(JSON)  # Array of document URLs/references

    # Relationships
    equipment = relationship("EquipmentMaster", back_populates="history")
    performed_by = relationship("User", foreign_keys=[performed_by_id])
    verified_by = relationship("User", foreign_keys=[verified_by_id])


class EquipmentUtilization(Base):
    """Track equipment usage for utilization and OEE calculations"""
    __tablename__ = "equipment_utilization"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id"), nullable=False, index=True)

    # Time tracking
    date = Column(Date, nullable=False, index=True)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))

    # OEE Components
    planned_production_time = Column(Numeric(10, 2))  # minutes
    actual_production_time = Column(Numeric(10, 2))  # minutes
    downtime = Column(Numeric(10, 2))  # minutes

    # Downtime breakdown
    calibration_downtime = Column(Numeric(10, 2), default=0)
    maintenance_downtime = Column(Numeric(10, 2), default=0)
    breakdown_downtime = Column(Numeric(10, 2), default=0)
    idle_time = Column(Numeric(10, 2), default=0)

    # Performance metrics
    ideal_cycle_time = Column(Numeric(10, 2))
    total_count = Column(Integer)  # Total pieces produced/tested
    good_count = Column(Integer)  # Good pieces
    reject_count = Column(Integer)  # Rejected pieces

    # Calculated OEE (will be calculated)
    availability = Column(Numeric(5, 2))  # Percentage
    performance = Column(Numeric(5, 2))  # Percentage
    quality = Column(Numeric(5, 2))  # Percentage
    oee = Column(Numeric(5, 2))  # Overall Equipment Effectiveness

    # User and notes
    operator_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    equipment = relationship("EquipmentMaster", back_populates="utilization_records")
    operator = relationship("User")
