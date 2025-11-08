"""
Maintenance models for preventive and corrective maintenance
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


class MaintenanceType(str, enum.Enum):
    """Maintenance type"""
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    BREAKDOWN = "breakdown"
    PREDICTIVE = "predictive"


class MaintenancePriority(str, enum.Enum):
    """Maintenance priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MaintenanceStatus(str, enum.Enum):
    """Maintenance status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class PreventiveMaintenanceSchedule(Base):
    """Preventive maintenance schedule for equipment"""
    __tablename__ = "preventive_maintenance_schedule"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id"), nullable=False, index=True)

    # Schedule details
    schedule_name = Column(String(255), nullable=False)
    description = Column(Text)
    frequency = Column(String(50), nullable=False)  # weekly, monthly, quarterly, yearly
    frequency_days = Column(Integer)  # Convert frequency to days for calculation

    # Timeline
    start_date = Column(Date, nullable=False)
    last_performed_date = Column(Date)
    next_due_date = Column(Date, nullable=False, index=True)

    # Task checklist
    checklist_items = Column(JSON)  # Array of maintenance tasks
    estimated_duration_hours = Column(Numeric(5, 2))

    # Resources required
    required_parts = Column(JSON)
    required_tools = Column(JSON)
    assigned_technician_id = Column(Integer, ForeignKey("users.id"))

    # Status
    is_active = Column(Boolean, default=True)
    is_overdue = Column(Boolean, default=False)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    equipment = relationship("EquipmentMaster")
    assigned_technician = relationship("User", foreign_keys=[assigned_technician_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    maintenance_records = relationship("MaintenanceRecord", back_populates="schedule")


class MaintenanceRecord(Base):
    """Maintenance records for all types of maintenance"""
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, index=True)

    # Unique maintenance ID
    maintenance_id = Column(String(50), unique=True, nullable=False, index=True)

    # Link to equipment and schedule
    equipment_id = Column(Integer, ForeignKey("equipment_master.id"), nullable=False, index=True)
    schedule_id = Column(Integer, ForeignKey("preventive_maintenance_schedule.id"))

    # Maintenance details
    maintenance_type = Column(SQLEnum(MaintenanceType), nullable=False)
    priority = Column(SQLEnum(MaintenancePriority), nullable=False, default=MaintenancePriority.MEDIUM)
    status = Column(SQLEnum(MaintenanceStatus), nullable=False, default=MaintenanceStatus.SCHEDULED)

    # Timeline
    scheduled_date = Column(Date, index=True)
    start_datetime = Column(DateTime(timezone=True))
    end_datetime = Column(DateTime(timezone=True))
    actual_duration_hours = Column(Numeric(5, 2))

    # Problem and solution
    problem_description = Column(Text)
    work_performed = Column(Text)
    parts_replaced = Column(JSON)  # Array of parts with details
    parts_cost = Column(Numeric(15, 2))

    # People involved
    performed_by_id = Column(Integer, ForeignKey("users.id"))
    supervised_by_id = Column(Integer, ForeignKey("users.id"))
    verified_by_id = Column(Integer, ForeignKey("users.id"))

    # Workflow
    workflow_status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    workflow_id = Column(Integer, ForeignKey("workflow_records.id"))

    # Cost tracking
    labor_cost = Column(Numeric(15, 2))
    service_cost = Column(Numeric(15, 2))
    total_cost = Column(Numeric(15, 2))

    # Vendor (if external service)
    service_vendor = Column(String(255))
    vendor_invoice_number = Column(String(100))

    # Downtime tracking
    downtime_hours = Column(Numeric(10, 2))
    production_loss = Column(Numeric(15, 2))

    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    follow_up_notes = Column(Text)

    # Attachments
    attachment_urls = Column(JSON)  # Array of document URLs
    before_photos = Column(JSON)
    after_photos = Column(JSON)

    # Recommendations
    recommendations = Column(Text)
    preventive_action = Column(Text)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    equipment = relationship("EquipmentMaster", back_populates="maintenance_records")
    schedule = relationship("PreventiveMaintenanceSchedule", back_populates="maintenance_records")
    workflow = relationship("WorkflowRecord")
    performed_by = relationship("User", foreign_keys=[performed_by_id])
    supervised_by = relationship("User", foreign_keys=[supervised_by_id])
    verified_by = relationship("User", foreign_keys=[verified_by_id])
    created_by = relationship("User", foreign_keys=[created_by_id])


class EquipmentFailureLog(Base):
    """Log of equipment failures for AI pattern detection"""
    __tablename__ = "equipment_failure_log"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment_master.id"), nullable=False, index=True)

    # Failure details
    failure_date = Column(DateTime(timezone=True), nullable=False, index=True)
    failure_type = Column(String(100), nullable=False)
    failure_description = Column(Text, nullable=False)
    severity = Column(String(20))  # minor, moderate, major, critical

    # Conditions at failure
    usage_hours_at_failure = Column(Numeric(10, 2))
    days_since_last_calibration = Column(Integer)
    days_since_last_maintenance = Column(Integer)
    environmental_conditions = Column(JSON)

    # Root cause analysis
    root_cause = Column(Text)
    contributing_factors = Column(JSON)

    # Impact
    downtime_hours = Column(Numeric(10, 2))
    affected_tests = Column(Integer)
    financial_impact = Column(Numeric(15, 2))

    # Resolution
    resolved_by_maintenance_id = Column(Integer, ForeignKey("maintenance_records.id"))
    resolution_date = Column(DateTime(timezone=True))

    # AI analysis flags
    is_analyzed = Column(Boolean, default=False)
    pattern_detected = Column(String(255))
    predicted_next_failure = Column(Date)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    equipment = relationship("EquipmentMaster")
    resolved_by_maintenance = relationship("MaintenanceRecord")
    created_by = relationship("User")
