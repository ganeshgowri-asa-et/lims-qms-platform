"""
Session management schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SessionResponse(BaseModel):
    """Session response schema"""
    id: int
    session_token: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    location: Optional[str] = None
    status: str
    login_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    is_current: bool = False
    is_suspicious: bool = False

    class Config:
        from_attributes = True


class SessionList(BaseModel):
    """Session list response"""
    total: int
    active_sessions: int
    sessions: List[SessionResponse]


class SessionTerminate(BaseModel):
    """Terminate session request"""
    session_id: Optional[int] = None
    terminate_all: bool = False
    reason: Optional[str] = None


class LoginHistoryResponse(BaseModel):
    """Login history response"""
    id: int
    username: str
    success: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[str] = None
    failure_reason: Optional[str] = None
    attempted_at: datetime

    class Config:
        from_attributes = True


class LoginHistoryList(BaseModel):
    """Login history list response"""
    total: int
    page: int
    page_size: int
    history: List[LoginHistoryResponse]


class SessionSearchRequest(BaseModel):
    """Session search request"""
    user_id: Optional[int] = None
    status: Optional[str] = None
    is_suspicious: Optional[bool] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
