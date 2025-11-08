"""
Pydantic schemas for Authentication and Users
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    role: str = "viewer"
    phone_number: Optional[str] = None
    department: Optional[str] = None
    employee_id: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class DigitalSignatureCreate(BaseModel):
    """Digital signature for workflow approvals"""
    signature_data: str  # Base64 encoded signature image
    password: str  # User password for verification


class DigitalSignatureResponse(BaseModel):
    user_id: int
    username: str
    timestamp: datetime
    signature_hash: str
