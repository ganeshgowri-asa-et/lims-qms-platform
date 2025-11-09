"""
Security utilities for authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Optional, Union, Any, Dict, List
from jose import JWTError, jwt
from passlib.context import CryptContext
import pyotp
import qrcode
import io
import base64
import secrets
import string
import hashlib
import re
from cryptography.fernet import Fernet
from .config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption (for MFA secrets, SSO tokens, etc.)
# Note: In production, use settings.ENCRYPTION_KEY from environment
ENCRYPTION_KEY = getattr(settings, 'ENCRYPTION_KEY', Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY if isinstance(ENCRYPTION_KEY, bytes) else ENCRYPTION_KEY.encode())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token

    Args:
        token: JWT token to decode

    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def create_refresh_token(data: dict) -> str:
    """
    Create a refresh token with longer expiration

    Args:
        data: Data to encode in the token

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)  # 30 days for refresh token
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


# ========================================
# PASSWORD POLICY AND VALIDATION
# ========================================

class PasswordPolicy:
    """Password policy configuration"""
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    MIN_UNIQUE_CHARS = 5
    PREVENT_REUSE_COUNT = 5  # Prevent reusing last N passwords
    MAX_AGE_DAYS = 90  # Force password change after N days
    SPECIAL_CHARS = "!@#$%^&*(),.?\":{}|<>"


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password against security policy

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < PasswordPolicy.MIN_LENGTH:
        return False, f"Password must be at least {PasswordPolicy.MIN_LENGTH} characters long"

    if len(password) > PasswordPolicy.MAX_LENGTH:
        return False, f"Password must be at most {PasswordPolicy.MAX_LENGTH} characters long"

    if PasswordPolicy.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if PasswordPolicy.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if PasswordPolicy.REQUIRE_DIGIT and not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"

    if PasswordPolicy.REQUIRE_SPECIAL and not re.search(f'[{re.escape(PasswordPolicy.SPECIAL_CHARS)}]', password):
        return False, f"Password must contain at least one special character ({PasswordPolicy.SPECIAL_CHARS})"

    if len(set(password)) < PasswordPolicy.MIN_UNIQUE_CHARS:
        return False, f"Password must contain at least {PasswordPolicy.MIN_UNIQUE_CHARS} unique characters"

    # Check for common patterns
    if re.search(r'(.)\1{2,}', password):  # Same character repeated 3+ times
        return False, "Password contains repeated characters"

    if re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def)', password.lower()):
        return False, "Password contains sequential characters"

    # Check for common words
    common_passwords = ['password', 'admin', 'user', 'test', '1234', 'qwerty', 'letmein']
    if any(common in password.lower() for common in common_passwords):
        return False, "Password contains common words or patterns"

    return True, None


def check_password_expiry(password_changed_at: Optional[datetime]) -> tuple[bool, Optional[int]]:
    """
    Check if password has expired

    Args:
        password_changed_at: When password was last changed

    Returns:
        Tuple of (is_expired, days_until_expiry)
    """
    if not password_changed_at:
        return True, 0

    age = datetime.utcnow() - password_changed_at
    days_old = age.days
    days_until_expiry = PasswordPolicy.MAX_AGE_DAYS - days_old

    is_expired = days_old >= PasswordPolicy.MAX_AGE_DAYS
    return is_expired, days_until_expiry


# ========================================
# MULTI-FACTOR AUTHENTICATION (MFA)
# ========================================

def generate_totp_secret() -> str:
    """Generate a random TOTP secret"""
    return pyotp.random_base32()


def generate_totp_uri(secret: str, username: str, issuer: str = "LIMS-QMS") -> str:
    """
    Generate TOTP provisioning URI for QR code

    Args:
        secret: TOTP secret
        username: User's username or email
        issuer: Application name

    Returns:
        TOTP provisioning URI
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name=issuer)


def generate_qr_code(data: str) -> str:
    """
    Generate QR code image as base64 string

    Args:
        data: Data to encode in QR code

    Returns:
        Base64 encoded QR code image
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    """
    Verify TOTP code

    Args:
        secret: TOTP secret
        code: Code to verify
        window: Time window for verification (default 1 = ±30 seconds)

    Returns:
        True if code is valid
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=window)


def generate_backup_codes(count: int = 10) -> List[str]:
    """
    Generate backup codes for MFA recovery

    Args:
        count: Number of codes to generate

    Returns:
        List of backup codes
    """
    codes = []
    for _ in range(count):
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        # Format as XXXX-XXXX
        formatted_code = f"{code[:4]}-{code[4:]}"
        codes.append(formatted_code)
    return codes


def hash_backup_code(code: str) -> str:
    """Hash a backup code for storage"""
    return hashlib.sha256(code.encode()).hexdigest()


def verify_backup_code(code: str, hashed_codes: List[str]) -> bool:
    """
    Verify backup code against list of hashed codes

    Args:
        code: Code to verify
        hashed_codes: List of hashed backup codes

    Returns:
        True if code is valid
    """
    code_hash = hash_backup_code(code)
    return code_hash in hashed_codes


# ========================================
# ENCRYPTION AND DECRYPTION
# ========================================

def encrypt_data(data: str) -> str:
    """
    Encrypt sensitive data

    Args:
        data: Data to encrypt

    Returns:
        Encrypted data as string
    """
    if not data:
        return ""
    encrypted = cipher_suite.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> Optional[str]:
    """
    Decrypt sensitive data

    Args:
        encrypted_data: Encrypted data

    Returns:
        Decrypted data or None if decryption fails
    """
    if not encrypted_data:
        return None
    try:
        decoded = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = cipher_suite.decrypt(decoded)
        return decrypted.decode()
    except Exception:
        return None


# ========================================
# API KEY GENERATION AND VALIDATION
# ========================================

def generate_api_key() -> tuple[str, str, str]:
    """
    Generate a random API key

    Returns:
        Tuple of (full_key, key_hash, key_prefix)
    """
    # Generate random key
    key = secrets.token_urlsafe(32)
    prefix = key[:8]

    # Hash for storage
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    return key, key_hash, prefix


def verify_api_key(provided_key: str, stored_hash: str) -> bool:
    """
    Verify API key against stored hash

    Args:
        provided_key: API key provided by user
        stored_hash: Stored hash of the key

    Returns:
        True if key is valid
    """
    key_hash = hashlib.sha256(provided_key.encode()).hexdigest()
    return key_hash == stored_hash


# ========================================
# SECURITY UTILITIES
# ========================================

def generate_random_token(length: int = 32) -> str:
    """Generate a random secure token"""
    return secrets.token_urlsafe(length)


def generate_session_token() -> str:
    """Generate a session token"""
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    """Hash a token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()


def check_ip_whitelist(ip_address: str, whitelist: List[str]) -> bool:
    """
    Check if IP address is in whitelist

    Args:
        ip_address: IP address to check
        whitelist: List of allowed IP addresses/ranges

    Returns:
        True if IP is whitelisted
    """
    if not whitelist:
        return True  # No whitelist = allow all

    # Simple implementation - can be enhanced with CIDR support
    return ip_address in whitelist


def calculate_risk_score(activity: Dict[str, Any]) -> int:
    """
    Calculate risk score for user activity

    Args:
        activity: Activity details

    Returns:
        Risk score (0-100)
    """
    score = 0

    # Failed login attempts
    if activity.get('activity_type') == 'LOGIN_FAILED':
        score += 30

    # Suspicious IP
    if activity.get('is_new_ip'):
        score += 20

    # Unusual time
    if activity.get('is_unusual_time'):
        score += 15

    # Multiple rapid requests
    if activity.get('rapid_requests'):
        score += 25

    # Sensitive resource access
    if activity.get('is_sensitive_resource'):
        score += 10

    return min(score, 100)


def is_account_locked(failed_attempts: int, locked_until: Optional[datetime]) -> tuple[bool, Optional[str]]:
    """
    Check if account is locked due to failed login attempts

    Args:
        failed_attempts: Number of failed login attempts
        locked_until: Timestamp until which account is locked

    Returns:
        Tuple of (is_locked, reason)
    """
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30

    if locked_until and datetime.utcnow() < locked_until:
        remaining = (locked_until - datetime.utcnow()).seconds // 60
        return True, f"Account is locked for {remaining} more minutes due to multiple failed login attempts"

    if failed_attempts >= MAX_FAILED_ATTEMPTS:
        return True, "Account is locked due to too many failed login attempts. Please contact administrator."

    return False, None


def calculate_lockout_time(failed_attempts: int) -> Optional[datetime]:
    """
    Calculate account lockout time based on failed attempts

    Args:
        failed_attempts: Number of failed login attempts

    Returns:
        Lockout end time or None
    """
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30

    if failed_attempts >= MAX_FAILED_ATTEMPTS:
        return datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)

    return None
