"""
Activity Logging and Audit Service
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import Request
from ..models.user import User, UserActivity, ActivityType
from ..core.security import calculate_risk_score


class ActivityService:
    """Service for logging user activities and audit trail"""

    @staticmethod
    def log_activity(
        db: Session,
        user: Optional[User],
        activity_type: ActivityType,
        action: str,
        description: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        request: Optional[Request] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_suspicious: bool = False
    ) -> UserActivity:
        """
        Log a user activity

        Args:
            db: Database session
            user: User performing the activity (None for failed logins)
            activity_type: Type of activity
            action: Action performed
            description: Activity description
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            request: FastAPI request object
            changes: Before/after changes
            metadata: Additional metadata
            is_suspicious: Mark as suspicious activity

        Returns:
            Created UserActivity object
        """
        # Extract request details if available
        ip_address = None
        user_agent = None
        request_method = None
        request_path = None

        if request:
            ip_address = ActivityService._get_client_ip(request)
            user_agent = request.headers.get('user-agent')
            request_method = request.method
            request_path = str(request.url.path)

        # Calculate risk score
        activity_data = {
            'activity_type': activity_type.value if isinstance(activity_type, ActivityType) else activity_type,
            'is_new_ip': False,  # TODO: Implement IP tracking
            'is_unusual_time': False,  # TODO: Implement time analysis
            'rapid_requests': False,  # TODO: Implement rate limiting check
            'is_sensitive_resource': resource_type in ['user', 'role', 'permission', 'api_key']
        }
        risk_score = calculate_risk_score(activity_data)

        # Create activity log
        activity = UserActivity(
            user_id=user.id if user else None,
            username=user.username if user else metadata.get('username') if metadata else None,
            activity_type=activity_type,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            action=action,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path,
            changes=changes,
            metadata=metadata,
            is_suspicious=is_suspicious or risk_score > 50,
            risk_score=risk_score,
            occurred_at=datetime.utcnow()
        )

        db.add(activity)
        db.commit()
        db.refresh(activity)

        return activity

    @staticmethod
    def log_login(
        db: Session,
        user: User,
        success: bool,
        request: Optional[Request] = None,
        failure_reason: Optional[str] = None
    ):
        """
        Log login attempt

        Args:
            db: Database session
            user: User attempting login
            success: Whether login was successful
            request: FastAPI request object
            failure_reason: Reason for failure
        """
        activity_type = ActivityType.LOGIN if success else ActivityType.LOGIN_FAILED

        metadata = {}
        if not success and failure_reason:
            metadata['failure_reason'] = failure_reason

        ActivityService.log_activity(
            db=db,
            user=user if success else None,
            activity_type=activity_type,
            action='login',
            description=f"User {'logged in successfully' if success else 'login failed'}",
            request=request,
            metadata=metadata,
            is_suspicious=not success
        )

    @staticmethod
    def log_logout(db: Session, user: User, request: Optional[Request] = None):
        """
        Log logout

        Args:
            db: Database session
            user: User logging out
            request: FastAPI request object
        """
        ActivityService.log_activity(
            db=db,
            user=user,
            activity_type=ActivityType.LOGOUT,
            action='logout',
            description="User logged out",
            request=request
        )

    @staticmethod
    def log_password_change(
        db: Session,
        user: User,
        changed_by: Optional[User] = None,
        request: Optional[Request] = None
    ):
        """
        Log password change

        Args:
            db: Database session
            user: User whose password was changed
            changed_by: User who changed the password (for admin resets)
            request: FastAPI request object
        """
        is_self_change = changed_by is None or changed_by.id == user.id

        ActivityService.log_activity(
            db=db,
            user=changed_by or user,
            activity_type=ActivityType.PASSWORD_CHANGE,
            action='change_password',
            description=f"Password changed for user {user.username}" +
                       (" (self-service)" if is_self_change else f" by {changed_by.username}"),
            resource_type='user',
            resource_id=str(user.id),
            request=request,
            metadata={'target_user': user.username, 'self_change': is_self_change}
        )

    @staticmethod
    def log_permission_change(
        db: Session,
        user: User,
        target_user: User,
        action: str,
        changes: Dict[str, Any],
        request: Optional[Request] = None
    ):
        """
        Log permission or role change

        Args:
            db: Database session
            user: User making the change
            target_user: User whose permissions are being changed
            action: Type of change
            changes: Details of changes
            request: FastAPI request object
        """
        ActivityService.log_activity(
            db=db,
            user=user,
            activity_type=ActivityType.PERMISSION_CHANGE,
            action=action,
            description=f"Permissions changed for user {target_user.username}",
            resource_type='user',
            resource_id=str(target_user.id),
            request=request,
            changes=changes,
            metadata={'target_user': target_user.username}
        )

    @staticmethod
    def log_resource_access(
        db: Session,
        user: User,
        resource_type: str,
        resource_id: str,
        action: str,
        request: Optional[Request] = None,
        changes: Optional[Dict[str, Any]] = None
    ):
        """
        Log resource access (create, read, update, delete)

        Args:
            db: Database session
            user: User accessing resource
            resource_type: Type of resource
            resource_id: Resource ID
            action: Action performed
            request: FastAPI request object
            changes: Changes made (for updates)
        """
        ActivityService.log_activity(
            db=db,
            user=user,
            activity_type=ActivityType.PROFILE_UPDATE,  # Generic activity type
            action=action,
            description=f"User {action}d {resource_type} {resource_id}",
            resource_type=resource_type,
            resource_id=resource_id,
            request=request,
            changes=changes
        )

    @staticmethod
    def log_api_key_action(
        db: Session,
        user: User,
        action: str,
        api_key_id: int,
        request: Optional[Request] = None
    ):
        """
        Log API key creation or revocation

        Args:
            db: Database session
            user: User performing action
            action: 'created' or 'revoked'
            api_key_id: API key ID
            request: FastAPI request object
        """
        activity_type = ActivityType.API_KEY_CREATED if action == 'created' else ActivityType.API_KEY_REVOKED

        ActivityService.log_activity(
            db=db,
            user=user,
            activity_type=activity_type,
            action=action,
            description=f"API key {action}",
            resource_type='api_key',
            resource_id=str(api_key_id),
            request=request
        )

    @staticmethod
    def log_mfa_action(
        db: Session,
        user: User,
        action: str,
        request: Optional[Request] = None
    ):
        """
        Log MFA enabled/disabled

        Args:
            db: Database session
            user: User performing action
            action: 'enabled' or 'disabled'
            request: FastAPI request object
        """
        activity_type = ActivityType.MFA_ENABLED if action == 'enabled' else ActivityType.MFA_DISABLED

        ActivityService.log_activity(
            db=db,
            user=user,
            activity_type=activity_type,
            action=action,
            description=f"MFA {action} for user {user.username}",
            resource_type='user',
            resource_id=str(user.id),
            request=request
        )

    @staticmethod
    def log_suspicious_activity(
        db: Session,
        user: Optional[User],
        description: str,
        request: Optional[Request] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log suspicious activity

        Args:
            db: Database session
            user: User involved (if known)
            description: Description of suspicious activity
            request: FastAPI request object
            metadata: Additional context
        """
        ActivityService.log_activity(
            db=db,
            user=user,
            activity_type=ActivityType.SUSPICIOUS_ACTIVITY,
            action='suspicious',
            description=description,
            request=request,
            metadata=metadata,
            is_suspicious=True
        )

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """
        Extract client IP from request

        Args:
            request: FastAPI request object

        Returns:
            Client IP address
        """
        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()

        # Check for real IP (some proxies)
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip

        # Fall back to client host
        if request.client:
            return request.client.host

        return 'unknown'

    @staticmethod
    def get_user_activity_summary(db: Session, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get activity summary for a user

        Args:
            db: Database session
            user_id: User ID
            days: Number of days to look back

        Returns:
            Activity summary dict
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        activities = db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.occurred_at >= cutoff_date
        ).all()

        # Group by activity type
        by_type = {}
        for activity in activities:
            activity_type = activity.activity_type.value
            by_type[activity_type] = by_type.get(activity_type, 0) + 1

        return {
            'total_activities': len(activities),
            'by_type': by_type,
            'suspicious_count': sum(1 for a in activities if a.is_suspicious),
            'date_range': {
                'from': cutoff_date,
                'to': datetime.utcnow()
            }
        }


# Import for type hints
from datetime import timedelta
