"""
Pydantic schemas for Test Request API
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class TestParameterBase(BaseModel):
    """Base test parameter schema"""
    parameter_name: str
    parameter_code: Optional[str] = None
    test_method: Optional[str] = None
    specification: Optional[str] = None
    unit_of_measurement: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    quantity: int = 1


class TestParameterCreate(TestParameterBase):
    """Schema for creating a test parameter"""
    pass


class TestParameterResponse(TestParameterBase):
    """Schema for test parameter response"""
    id: int
    test_request_id: int
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    result: Optional[str] = None
    pass_fail: Optional[str] = None
    is_completed: bool = False

    class Config:
        from_attributes = True


class TestRequestBase(BaseModel):
    """Base test request schema"""
    customer_id: int
    project_name: str
    test_type: str
    priority: str = "medium"
    request_date: date
    due_date: Optional[date] = None
    description: Optional[str] = None
    special_instructions: Optional[str] = None
    requested_by: str
    department: Optional[str] = None
    contact_number: Optional[str] = None
    quote_required: bool = False


class TestRequestCreate(TestRequestBase):
    """Schema for creating a test request"""
    created_by: str
    test_parameters: Optional[List[TestParameterCreate]] = []


class TestRequestUpdate(BaseModel):
    """Schema for updating a test request"""
    project_name: Optional[str] = None
    test_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    completion_date: Optional[date] = None
    description: Optional[str] = None
    special_instructions: Optional[str] = None
    updated_by: Optional[str] = None


class TestRequestResponse(TestRequestBase):
    """Schema for test request response"""
    id: int
    trq_number: str
    status: str
    completion_date: Optional[date] = None
    quote_number: Optional[str] = None
    quote_amount: Optional[Decimal] = None
    quote_approved: bool = False
    barcode_data: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: str
    test_parameters: List[TestParameterResponse] = []

    class Config:
        from_attributes = True


class QuoteResponse(BaseModel):
    """Schema for quote response"""
    quote_number: str
    trq_number: str
    project_name: str
    total_amount: float
    priority: str
    parameters: List[dict]
    generated_date: str
