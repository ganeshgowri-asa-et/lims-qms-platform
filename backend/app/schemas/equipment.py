"""
Pydantic schemas for Equipment models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal


class EquipmentSpecificationBase(BaseModel):
    parameter_name: str
    measurement_range_min: Optional[Decimal] = None
    measurement_range_max: Optional[Decimal] = None
    unit: Optional[str] = None
    accuracy: Optional[str] = None
    resolution: Optional[str] = None
    uncertainty: Optional[str] = None
    specification_notes: Optional[str] = None


class EquipmentSpecificationCreate(EquipmentSpecificationBase):
    pass


class EquipmentSpecificationResponse(EquipmentSpecificationBase):
    id: int
    equipment_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EquipmentBase(BaseModel):
    equipment_name: str = Field(..., min_length=1, max_length=255)
    category: str
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    department: str
    location: str
    sub_location: Optional[str] = None
    responsible_person_id: Optional[int] = None
    supplier_vendor: Optional[str] = None
    purchase_order_number: Optional[str] = None
    purchase_date: Optional[date] = None
    installation_date: Optional[date] = None
    warranty_expiry_date: Optional[date] = None
    asset_value: Optional[Decimal] = None
    technical_specifications: Optional[Dict[str, Any]] = None
    operating_range: Optional[str] = None
    accuracy: Optional[str] = None
    resolution: Optional[str] = None
    requires_calibration: bool = True
    calibration_frequency: Optional[str] = None
    calibration_standard_reference: Optional[str] = None
    maintenance_frequency: Optional[str] = None
    status: str = "operational"
    is_critical: bool = False
    user_manual_url: Optional[str] = None
    sop_reference: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    specifications: Optional[List[EquipmentSpecificationCreate]] = []


class EquipmentUpdate(BaseModel):
    equipment_name: Optional[str] = None
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None
    location: Optional[str] = None
    sub_location: Optional[str] = None
    responsible_person_id: Optional[int] = None
    status: Optional[str] = None
    operating_range: Optional[str] = None
    accuracy: Optional[str] = None
    resolution: Optional[str] = None
    calibration_frequency: Optional[str] = None
    maintenance_frequency: Optional[str] = None
    technical_specifications: Optional[Dict[str, Any]] = None


class EquipmentResponse(EquipmentBase):
    id: int
    equipment_id: str  # EQP-DEPT-YYYY-XXX
    equipment_code: Optional[str] = None
    qr_code_data: Optional[str] = None
    qr_code_url: Optional[str] = None
    last_calibration_date: Optional[date] = None
    next_calibration_date: Optional[date] = None
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    usage_hours: Optional[Decimal] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    specifications: List[EquipmentSpecificationResponse] = []

    class Config:
        from_attributes = True


class EquipmentListResponse(BaseModel):
    items: List[EquipmentResponse]
    total: int
    page: int
    page_size: int


class EquipmentHistoryBase(BaseModel):
    event_type: str
    description: str
    before_status: Optional[str] = None
    after_status: Optional[str] = None
    downtime_hours: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    supporting_documents: Optional[Dict[str, Any]] = None


class EquipmentHistoryCreate(EquipmentHistoryBase):
    equipment_id: int
    performed_by_id: int
    verified_by_id: Optional[int] = None


class EquipmentHistoryResponse(EquipmentHistoryBase):
    id: int
    equipment_id: int
    event_date: datetime
    performed_by_id: Optional[int] = None
    verified_by_id: Optional[int] = None

    class Config:
        from_attributes = True


class EquipmentUtilizationBase(BaseModel):
    date: date
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    planned_production_time: Optional[Decimal] = None
    actual_production_time: Optional[Decimal] = None
    downtime: Optional[Decimal] = None
    calibration_downtime: Optional[Decimal] = 0
    maintenance_downtime: Optional[Decimal] = 0
    breakdown_downtime: Optional[Decimal] = 0
    idle_time: Optional[Decimal] = 0
    ideal_cycle_time: Optional[Decimal] = None
    total_count: Optional[int] = None
    good_count: Optional[int] = None
    reject_count: Optional[int] = None
    operator_id: Optional[int] = None
    notes: Optional[str] = None


class EquipmentUtilizationCreate(EquipmentUtilizationBase):
    equipment_id: int


class EquipmentUtilizationResponse(EquipmentUtilizationBase):
    id: int
    equipment_id: int
    availability: Optional[Decimal] = None
    performance: Optional[Decimal] = None
    quality: Optional[Decimal] = None
    oee: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OEECalculationResponse(BaseModel):
    equipment_id: int
    equipment_name: str
    period_start: date
    period_end: date
    average_availability: Decimal
    average_performance: Decimal
    average_quality: Decimal
    average_oee: Decimal
    total_downtime_hours: Decimal
    breakdown_by_type: Dict[str, Decimal]
