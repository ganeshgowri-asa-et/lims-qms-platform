"""
Pydantic schemas for Sample API
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class SampleBase(BaseModel):
    """Base sample schema"""
    test_request_id: int
    sample_name: str
    sample_type: str
    sample_description: Optional[str] = None
    quantity: Decimal
    unit: str
    condition_on_receipt: Optional[str] = None
    storage_condition: Optional[str] = None
    expiry_date: Optional[date] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    manufacturing_date: Optional[date] = None
    storage_location: Optional[str] = None
    remarks: Optional[str] = None


class SampleCreate(SampleBase):
    """Schema for creating a sample"""
    created_by: str


class SampleUpdate(BaseModel):
    """Schema for updating a sample"""
    sample_name: Optional[str] = None
    sample_type: Optional[str] = None
    sample_description: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    status: Optional[str] = None
    condition_on_receipt: Optional[str] = None
    storage_condition: Optional[str] = None
    expiry_date: Optional[date] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    manufacturing_date: Optional[date] = None
    received_date: Optional[date] = None
    received_by: Optional[str] = None
    testing_start_date: Optional[date] = None
    testing_end_date: Optional[date] = None
    storage_location: Optional[str] = None
    remarks: Optional[str] = None
    updated_by: Optional[str] = None


class SampleResponse(SampleBase):
    """Schema for sample response"""
    id: int
    sample_number: str
    status: str
    received_date: Optional[date] = None
    received_by: Optional[str] = None
    testing_start_date: Optional[date] = None
    testing_end_date: Optional[date] = None
    barcode_data: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True
