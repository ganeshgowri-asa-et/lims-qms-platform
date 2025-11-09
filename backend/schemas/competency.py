"""
Competency and qualification schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CompetencyBase(BaseModel):
    """Base competency schema"""
    competency_type: str = Field(..., regex='^(certification|training|equipment|test_method)$')
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None


class CompetencyCreate(CompetencyBase):
    """Create competency schema"""
    issuing_authority: Optional[str] = Field(None, max_length=255)
    certificate_number: Optional[str] = Field(None, max_length=100)
    document_path: Optional[str] = None
    equipment_id: Optional[str] = None
    test_method_id: Optional[str] = None
    approval_level: int = Field(1, ge=1, le=5)
    obtained_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class CompetencyUpdate(BaseModel):
    """Update competency schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    issuing_authority: Optional[str] = None
    certificate_number: Optional[str] = None
    document_path: Optional[str] = None
    approval_level: Optional[int] = Field(None, ge=1, le=5)
    obtained_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_valid: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class CompetencyResponse(BaseModel):
    """Competency response schema"""
    id: int
    uuid: str
    user_id: int
    competency_type: str
    name: str
    description: Optional[str] = None
    issuing_authority: Optional[str] = None
    certificate_number: Optional[str] = None
    document_path: Optional[str] = None
    equipment_id: Optional[str] = None
    test_method_id: Optional[str] = None
    approval_level: int
    obtained_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_valid: bool
    verified_by_id: Optional[int] = None
    verified_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    days_until_expiry: Optional[int] = None

    class Config:
        from_attributes = True


class CompetencyList(BaseModel):
    """Competency list response"""
    total: int
    page: int
    page_size: int
    competencies: List[CompetencyResponse]


class CompetencyVerify(BaseModel):
    """Verify competency request"""
    is_valid: bool
    notes: Optional[str] = None


class CompetencySearchRequest(BaseModel):
    """Competency search request"""
    user_id: Optional[int] = None
    competency_type: Optional[str] = None
    equipment_id: Optional[str] = None
    test_method_id: Optional[str] = None
    is_valid: Optional[bool] = None
    expiring_soon: Optional[bool] = None  # Expiring within 30 days
    expired: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class CompetencyStats(BaseModel):
    """Competency statistics"""
    total_competencies: int
    valid_competencies: int
    expired_competencies: int
    expiring_soon: int
    by_type: Dict[str, int]
    by_user: List[Dict[str, Any]]


class EquipmentAuthorizationCheck(BaseModel):
    """Check equipment authorization"""
    user_id: int
    equipment_id: str


class EquipmentAuthorizationResponse(BaseModel):
    """Equipment authorization response"""
    authorized: bool
    approval_level: Optional[int] = None
    competency: Optional[CompetencyResponse] = None
    reason: Optional[str] = None


class CompetencyExpiryAlert(BaseModel):
    """Competency expiry alert"""
    competency_id: int
    user_id: int
    user_name: str
    competency_name: str
    expiry_date: datetime
    days_until_expiry: int
