"""
Pydantic schemas for Calibration models
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal


class CalibrationVendorBase(BaseModel):
    vendor_name: str = Field(..., min_length=1, max_length=255)
    vendor_code: Optional[str] = None
    vendor_contact_person: Optional[str] = None
    vendor_email: Optional[EmailStr] = None
    vendor_phone: Optional[str] = None
    vendor_address: Optional[str] = None
    accreditation_body: Optional[str] = None
    accreditation_number: Optional[str] = None
    accreditation_valid_until: Optional[date] = None
    scope_of_accreditation: Optional[str] = None
    is_approved: bool = False


class CalibrationVendorCreate(CalibrationVendorBase):
    pass


class CalibrationVendorUpdate(BaseModel):
    vendor_name: Optional[str] = None
    vendor_contact_person: Optional[str] = None
    vendor_email: Optional[EmailStr] = None
    vendor_phone: Optional[str] = None
    vendor_address: Optional[str] = None
    accreditation_body: Optional[str] = None
    accreditation_number: Optional[str] = None
    accreditation_valid_until: Optional[date] = None
    scope_of_accreditation: Optional[str] = None
    is_approved: Optional[bool] = None


class CalibrationVendorResponse(CalibrationVendorBase):
    id: int
    total_calibrations: int
    on_time_delivery_count: int
    delayed_delivery_count: int
    average_turnaround_days: Optional[Decimal] = None
    quality_rating: Optional[Decimal] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CalibrationRecordBase(BaseModel):
    equipment_id: int
    calibration_type: str
    calibration_date: date
    due_date: date
    vendor_id: Optional[int] = None
    certificate_number: Optional[str] = None
    certificate_issue_date: Optional[date] = None
    result: str
    result_details: Optional[str] = None
    as_found_data: Optional[Dict[str, Any]] = None
    as_left_data: Optional[Dict[str, Any]] = None
    uncertainty: Optional[str] = None
    environmental_conditions: Optional[Dict[str, Any]] = None
    reference_standards: Optional[Dict[str, Any]] = None
    traceability_chain: Optional[str] = None
    calibration_cost: Optional[Decimal] = None
    additional_charges: Optional[Decimal] = None
    action_taken: Optional[str] = None
    corrective_action: Optional[str] = None
    remarks: Optional[str] = None


class CalibrationRecordCreate(CalibrationRecordBase):
    performed_by_id: int


class CalibrationRecordUpdate(BaseModel):
    calibration_date: Optional[date] = None
    result: Optional[str] = None
    result_details: Optional[str] = None
    as_found_data: Optional[Dict[str, Any]] = None
    as_left_data: Optional[Dict[str, Any]] = None
    uncertainty: Optional[str] = None
    certificate_number: Optional[str] = None
    certificate_issue_date: Optional[date] = None
    calibration_cost: Optional[Decimal] = None
    additional_charges: Optional[Decimal] = None
    action_taken: Optional[str] = None
    corrective_action: Optional[str] = None
    remarks: Optional[str] = None


class CalibrationRecordResponse(CalibrationRecordBase):
    id: int
    calibration_id: str
    next_calibration_date: Optional[date] = None
    certificate_file_path: Optional[str] = None
    certificate_data: Optional[Dict[str, Any]] = None
    total_cost: Optional[Decimal] = None
    scheduled_date: Optional[date] = None
    sent_to_vendor_date: Optional[date] = None
    received_from_vendor_date: Optional[date] = None
    actual_calibration_date: Optional[date] = None
    turnaround_days: Optional[int] = None
    workflow_status: str
    performed_by_id: Optional[int] = None
    verified_by_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CalibrationRecordListResponse(BaseModel):
    items: List[CalibrationRecordResponse]
    total: int
    page: int
    page_size: int


class CalibrationScheduleBase(BaseModel):
    equipment_id: int
    scheduled_date: date
    calibration_type: Optional[str] = None
    preferred_vendor_id: Optional[int] = None
    notes: Optional[str] = None


class CalibrationScheduleCreate(CalibrationScheduleBase):
    pass


class CalibrationScheduleResponse(CalibrationScheduleBase):
    id: int
    is_completed: bool
    completed_calibration_id: Optional[int] = None
    is_overdue: bool
    alert_30_days_sent: bool
    alert_15_days_sent: bool
    alert_7_days_sent: bool
    alert_overdue_sent: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CalibrationDueListResponse(BaseModel):
    """Response for equipment calibrations due soon"""
    equipment_id: int
    equipment_name: str
    equipment_code: str
    department: str
    next_calibration_date: date
    days_until_due: int
    calibration_frequency: str
    last_calibration_date: Optional[date] = None
    is_overdue: bool
    alert_level: str  # "30_days", "15_days", "7_days", "overdue"


class CalibrationCertificateUpload(BaseModel):
    """Schema for certificate upload with OCR"""
    calibration_record_id: int
    file_content: str  # Base64 encoded file
    file_name: str
    extract_data: bool = True  # Whether to run OCR extraction


class CalibrationCertificateData(BaseModel):
    """Extracted data from calibration certificate"""
    certificate_number: Optional[str] = None
    calibration_date: Optional[date] = None
    due_date: Optional[date] = None
    equipment_serial: Optional[str] = None
    calibration_points: Optional[List[Dict[str, Any]]] = None
    uncertainty: Optional[str] = None
    standards_used: Optional[List[str]] = None
    environmental_conditions: Optional[Dict[str, str]] = None
    raw_text: Optional[str] = None
