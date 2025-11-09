"""
Pydantic schemas for Customer API
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CustomerBase(BaseModel):
    """Base customer schema"""
    customer_name: str
    customer_type: str
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = "India"
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    remarks: Optional[str] = None
    is_active: bool = True


class CustomerCreate(CustomerBase):
    """Schema for creating a customer"""
    created_by: str


class CustomerUpdate(BaseModel):
    """Schema for updating a customer"""
    customer_name: Optional[str] = None
    customer_type: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    remarks: Optional[str] = None
    is_active: Optional[bool] = None
    updated_by: Optional[str] = None


class CustomerResponse(CustomerBase):
    """Schema for customer response"""
    id: int
    customer_code: str
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True
