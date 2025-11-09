"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8)
    role: str = Field(default="user")


class UserResponse(UserBase):
    """Schema for user response"""
    user_id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data"""
    username: Optional[str] = None
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str
    password: str


class HealthCheck(BaseModel):
    """Schema for health check response"""
    status: str
    database: str
    timestamp: datetime
