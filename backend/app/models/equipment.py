"""
Equipment Calibration & Maintenance Models
"""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, DECIMAL, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class EquipmentMaster(Base):
    """Equipment Master table"""
    __tablename__ = "equipment_master"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    manufacturer = Column(String(200))
    model = Column(String(100))
    serial_number = Column(String(100))
    purchase_date = Column(Date)
    installation_date = Column(Date)
    location = Column(String(200))
    responsible_person = Column(String(100))
    status = Column(String(50), default="Active", index=True)
    qr_code_path = Column(String(500))
    specifications = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    calibrations = relationship("CalibrationRecord", back_populates="equipment")
    maintenance = relationship("PreventiveMaintenanceSchedule", back_populates="equipment")
    oee_records = relationship("OEETracking", back_populates="equipment")


class CalibrationRecord(Base):
    """Calibration Records"""
    __tablename__ = "calibration_records"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id", ondelete="CASCADE"))
    calibration_date = Column(Date, nullable=False)
    next_due_date = Column(Date, nullable=False, index=True)
    calibrated_by = Column(String(100), nullable=False)
    calibration_agency = Column(String(200))
    certificate_number = Column(String(100))
    certificate_path = Column(String(500))
    result = Column(String(50), default="Pass")
    remarks = Column(Text)
    notification_30_sent = Column(Boolean, default=False)
    notification_15_sent = Column(Boolean, default=False)
    notification_7_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    equipment = relationship("EquipmentMaster", back_populates="calibrations")


class PreventiveMaintenanceSchedule(Base):
    """Preventive Maintenance Schedule"""
    __tablename__ = "preventive_maintenance_schedule"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id", ondelete="CASCADE"))
    maintenance_type = Column(String(100), nullable=False)
    frequency = Column(String(50), nullable=False)
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date, nullable=False, index=True)
    performed_by = Column(String(100))
    status = Column(String(50), default="Scheduled")
    findings = Column(Text)
    actions_taken = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    equipment = relationship("EquipmentMaster", back_populates="maintenance")


class OEETracking(Base):
    """Overall Equipment Effectiveness Tracking"""
    __tablename__ = "oee_tracking"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    planned_production_time = Column(Integer)
    actual_production_time = Column(Integer)
    downtime_minutes = Column(Integer, default=0)
    units_produced = Column(Integer)
    defective_units = Column(Integer, default=0)
    availability_percent = Column(DECIMAL(5, 2))
    performance_percent = Column(DECIMAL(5, 2))
    quality_percent = Column(DECIMAL(5, 2))
    oee_percent = Column(DECIMAL(5, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    equipment = relationship("EquipmentMaster", back_populates="oee_records")
