"""
Equipment Calibration & Maintenance Models (Session 3)
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from backend.core.database import Base


class EquipmentStatus(str, enum.Enum):
    OPERATIONAL = "operational"
    UNDER_CALIBRATION = "under_calibration"
    UNDER_MAINTENANCE = "under_maintenance"
    OUT_OF_SERVICE = "out_of_service"


class CalibrationStatus(str, enum.Enum):
    DUE = "due"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class Equipment(Base):
    """Equipment master table"""
    __tablename__ = "equipment_master"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String(50), unique=True, nullable=False, index=True)  # EQP-XXX
    name = Column(String(200), nullable=False)
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))
    location = Column(String(100))
    status = Column(SQLEnum(EquipmentStatus), default=EquipmentStatus.OPERATIONAL)
    purchase_date = Column(Date)
    warranty_expiry = Column(Date)
    calibration_frequency_days = Column(Integer, default=365)
    last_calibration_date = Column(Date)
    next_calibration_date = Column(Date, index=True)
    responsible_person_id = Column(Integer, ForeignKey("users.id"))
    qr_code_path = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    calibration_records = relationship("CalibrationRecord", back_populates="equipment")
    maintenance_schedules = relationship("PreventiveMaintenanceSchedule", back_populates="equipment")


class CalibrationRecord(Base):
    """Calibration records table"""
    __tablename__ = "calibration_records"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id"), nullable=False)
    calibration_date = Column(Date, nullable=False)
    next_due_date = Column(Date, nullable=False)
    calibrated_by = Column(String(100), nullable=False)
    certificate_number = Column(String(100))
    calibration_standard = Column(String(200))
    result = Column(String(50))  # Pass/Fail
    remarks = Column(Text)
    certificate_path = Column(String(500))
    status = Column(SQLEnum(CalibrationStatus), default=CalibrationStatus.COMPLETED)
    performed_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    equipment = relationship("Equipment", back_populates="calibration_records")


class PreventiveMaintenanceSchedule(Base):
    """Preventive maintenance scheduling"""
    __tablename__ = "preventive_maintenance_schedule"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id"), nullable=False)
    maintenance_type = Column(String(100), nullable=False)
    frequency_days = Column(Integer, nullable=False)
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date, nullable=False, index=True)
    maintenance_checklist = Column(Text)  # JSON array
    performed_by_id = Column(Integer, ForeignKey("users.id"))
    completion_date = Column(Date)
    remarks = Column(Text)
    downtime_hours = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    equipment = relationship("Equipment", back_populates="maintenance_schedules")
