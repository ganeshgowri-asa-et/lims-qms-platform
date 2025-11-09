"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
import re


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # seconds
    mfa_required: bool = False
    mfa_token: Optional[str] = None  # Temporary token for MFA flow


class TokenData(BaseModel):
    """Token payload data"""
    user_id: int
    username: str
    email: str
    roles: List[str] = []
    permissions: List[str] = []
    session_id: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request"""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    mfa_code: Optional[str] = Field(None, min_length=6, max_length=6)
    remember_me: bool = False


class RegisterRequest(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=255)
    employee_id: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    designation: Optional[str] = Field(None, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate passwords match"""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate passwords match"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordChangeRequest(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate passwords match"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('new_password')
    def new_password_different(cls, v, values):
        """Ensure new password is different from current"""
        if 'current_password' in values and v == values['current_password']:
            raise ValueError('New password must be different from current password')
        return v


class MFASetupResponse(BaseModel):
    """MFA setup response"""
    secret: str
    qr_code: str  # Base64 encoded QR code image
    backup_codes: List[str]
    manual_entry_key: str


class MFAVerifyRequest(BaseModel):
    """MFA verification request"""
    code: str = Field(..., min_length=6, max_length=6)


class MFADisableRequest(BaseModel):
    """MFA disable request"""
    password: str
    code: Optional[str] = Field(None, min_length=6, max_length=6)


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout request"""
    logout_all_devices: bool = False


class APIKeyCreate(BaseModel):
    """Create API key request"""
    name: str = Field(..., min_length=3, max_length=255)
    scopes: Optional[List[str]] = None
    ip_whitelist: Optional[List[str]] = None
    expires_in_days: Optional[int] = Field(None, gt=0, le=365)


class APIKeyResponse(BaseModel):
    """API key response (only shown once)"""
    id: int
    name: str
    api_key: str  # Full key shown only on creation
    key_prefix: str
    scopes: Optional[List[str]] = None
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyList(BaseModel):
    """API key list item (without full key)"""
    id: int
    name: str
    key_prefix: str
    scopes: Optional[List[str]] = None
    is_active: bool
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SSOLoginRequest(BaseModel):
    """SSO login request"""
    provider: str  # 'google', 'microsoft', 'saml'
    code: Optional[str] = None
    state: Optional[str] = None


class SSOCallbackRequest(BaseModel):
    """SSO callback request"""
    code: str
    state: str
