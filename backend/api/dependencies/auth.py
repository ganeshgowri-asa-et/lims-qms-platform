"""
Authentication dependencies for FastAPI
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from backend.core import get_db, decode_access_token
from backend.core.security import is_account_locked, check_password_expiry, verify_api_key
from backend.models.user import User, UserSession, UserAPIKey, SessionStatus

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    request: Optional[Request] = None
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        token: JWT access token
        db: Database session
        request: FastAPI request object

    Returns:
        User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[int] = payload.get("sub")
    session_id: Optional[str] = payload.get("session_id")

    if user_id is None:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact administrator."
        )

    # Check if account is locked
    is_locked, lock_reason = is_account_locked(
        user.failed_login_attempts,
        user.account_locked_until
    )
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=lock_reason
        )

    # Check password expiry (warn but don't block)
    is_expired, days_until_expiry = check_password_expiry(user.password_changed_at)
    if user.force_password_change:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must change your password before continuing. Please use the password change endpoint."
        )

    # Validate session if session_id is provided
    if session_id:
        session = db.query(UserSession).filter(
            UserSession.session_token == session_id,
            UserSession.user_id == user.id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session. Please login again."
            )

        if session.status != SessionStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has been terminated. Please login again."
            )

        if session.expires_at < datetime.utcnow():
            session.status = SessionStatus.EXPIRED
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has expired. Please login again."
            )

        # Update last activity
        session.last_activity_at = datetime.utcnow()
        db.commit()

    # Update user last activity
    user.last_activity = datetime.utcnow()
    db.commit()

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user

    Args:
        current_user: Current authenticated user

    Returns:
        User object if active

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current superuser

    Args:
        current_user: Current authenticated user

    Returns:
        User object if superuser

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )
    return current_user


async def get_user_from_api_key(
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get user from API key

    Args:
        api_key: API key from header
        db: Database session

    Returns:
        User object if API key is valid, None otherwise

    Raises:
        HTTPException: If API key is invalid or expired
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Find API key
    api_key_obj = db.query(UserAPIKey).filter(
        UserAPIKey.is_active == True
    ).all()

    valid_key = None
    for key_obj in api_key_obj:
        if verify_api_key(api_key, key_obj.key_hash):
            valid_key = key_obj
            break

    if not valid_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Check expiration
    if valid_key.expires_at and valid_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Update usage
    valid_key.last_used_at = datetime.utcnow()
    valid_key.usage_count += 1
    db.commit()

    # Get user
    user = db.query(User).filter(User.id == valid_key.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return user


async def get_current_user_or_api_key(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from either JWT token or API key

    Args:
        token: JWT access token
        api_key: API key
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If neither token nor API key is valid
    """
    # Try JWT token first
    if token:
        try:
            return await get_current_user(token=token, db=db)
        except HTTPException:
            pass

    # Try API key
    if api_key:
        try:
            return await get_user_from_api_key(api_key=api_key, db=db)
        except HTTPException:
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Provide either a valid JWT token or API key.",
        headers={"WWW-Authenticate": "Bearer"},
    )
