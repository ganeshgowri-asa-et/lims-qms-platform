"""Pydantic schemas for equipment management."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..models.equipment import EquipmentStatus, CalibrationStatus, MaintenanceType


# Equipment Master Schemas
class EquipmentMasterBase(BaseModel):
    """Base schema for equipment."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    manufacturer: Optional[str] = Field(None, max_length=100)
    model_number: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    equipment_type: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    responsible_person: Optional[str] = Field(None, max_length=100)


class EquipmentMasterCreate(EquipmentMasterBase):
    """Schema for creating equipment."""
    purchase_date: Optional[datetime] = None
    purchase_cost: Optional[float] = None
    supplier: Optional[str] = Field(None, max_length=100)
    warranty_expiry: Optional[datetime] = None
    installation_date: Optional[datetime] = None
    commissioned_date: Optional[datetime] = None
    requires_calibration: bool = True
    calibration_frequency_days: int = Field(365, ge=1)
    maintenance_frequency_days: int = Field(180, ge=1)
    technical_specs: Optional[Dict[str, Any]] = None
    operating_range: Optional[Dict[str, Any]] = None


class EquipmentMasterUpdate(BaseModel):
    """Schema for updating equipment."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    manufacturer: Optional[str] = Field(None, max_length=100)
    model_number: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    responsible_person: Optional[str] = Field(None, max_length=100)
    status: Optional[EquipmentStatus] = None
    calibration_frequency_days: Optional[int] = Field(None, ge=1)
    maintenance_frequency_days: Optional[int] = Field(None, ge=1)


class EquipmentMasterResponse(EquipmentMasterBase):
    """Schema for equipment response."""
    id: int
    equipment_id: str
    status: EquipmentStatus
    purchase_date: Optional[datetime]
    purchase_cost: Optional[float]
    supplier: Optional[str]
    warranty_expiry: Optional[datetime]
    installation_date: Optional[datetime]
    commissioned_date: Optional[datetime]
    requires_calibration: bool
    calibration_frequency_days: int
    last_calibration_date: Optional[datetime]
    next_calibration_date: Optional[datetime]
    calibration_status: Optional[CalibrationStatus]
    maintenance_frequency_days: int
    last_maintenance_date: Optional[datetime]
    next_maintenance_date: Optional[datetime]
    oee_percentage: float
    availability_percentage: float
    performance_percentage: float
    quality_percentage: float
    qr_code_path: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Calibration Record Schemas
class CalibrationRecordBase(BaseModel):
    """Base schema for calibration records."""
    calibration_date: datetime
    next_calibration_date: datetime
    performed_by: str = Field(..., min_length=1, max_length=100)
    calibration_agency: Optional[str] = Field(None, max_length=100)
    certificate_number: Optional[str] = Field(None, max_length=100)


class CalibrationRecordCreate(CalibrationRecordBase):
    """Schema for creating calibration record."""
    equipment_id: int
    result: Optional[str] = Field(None, max_length=50)
    accuracy_achieved: Optional[float] = None
    uncertainty: Optional[float] = None
    reference_standard: Optional[str] = Field(None, max_length=100)
    standard_certificate_number: Optional[str] = Field(None, max_length=100)
    traceability: Optional[str] = Field(None, max_length=255)
    as_found_readings: Optional[Dict[str, Any]] = None
    as_left_readings: Optional[Dict[str, Any]] = None
    test_points: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    notes: Optional[str] = None


class CalibrationRecordResponse(CalibrationRecordBase):
    """Schema for calibration record response."""
    id: int
    equipment_id: int
    calibration_status: CalibrationStatus
    result: Optional[str]
    accuracy_achieved: Optional[float]
    uncertainty: Optional[float]
    reference_standard: Optional[str]
    traceability: Optional[str]
    certificate_path: Optional[str]
    report_path: Optional[str]
    reviewed_by: Optional[str]
    approved_by: Optional[str]
    reviewed_at: Optional[datetime]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Preventive Maintenance Schemas
class MaintenanceScheduleBase(BaseModel):
    """Base schema for maintenance schedule."""
    maintenance_type: MaintenanceType
    scheduled_date: datetime
    maintenance_description: str = Field(..., min_length=1)


class MaintenanceScheduleCreate(MaintenanceScheduleBase):
    """Schema for creating maintenance schedule."""
    equipment_id: int
    assigned_to: Optional[str] = Field(None, max_length=100)
    checklist: Optional[Dict[str, Any]] = None


class MaintenanceScheduleUpdate(BaseModel):
    """Schema for updating maintenance schedule."""
    completed_date: Optional[datetime] = None
    performed_by: Optional[str] = Field(None, max_length=100)
    parts_replaced: Optional[Dict[str, Any]] = None
    parts_cost: Optional[float] = None
    labor_hours: Optional[float] = None
    labor_cost: Optional[float] = None
    observations: Optional[str] = None
    issues_found: Optional[str] = None
    corrective_actions: Optional[str] = None
    is_completed: bool = False


class MaintenanceScheduleResponse(MaintenanceScheduleBase):
    """Schema for maintenance schedule response."""
    id: int
    equipment_id: int
    completed_date: Optional[datetime]
    is_completed: bool
    is_overdue: bool
    assigned_to: Optional[str]
    performed_by: Optional[str]
    parts_replaced: Optional[Dict[str, Any]]
    parts_cost: Optional[float]
    labor_hours: Optional[float]
    labor_cost: Optional[float]
    total_cost: Optional[float]
    observations: Optional[str]
    issues_found: Optional[str]
    corrective_actions: Optional[str]
    work_order_number: Optional[str]
    next_maintenance_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Alert Schemas
class CalibrationAlert(BaseModel):
    """Schema for calibration alerts."""
    equipment_id: str
    equipment_name: str
    next_calibration_date: datetime
    days_remaining: int
    alert_level: str  # critical (7 days), warning (15 days), info (30 days)


class MaintenanceAlert(BaseModel):
    """Schema for maintenance alerts."""
    equipment_id: str
    equipment_name: str
    next_maintenance_date: datetime
    days_remaining: int
    alert_level: str
