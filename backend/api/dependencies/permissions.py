"""
Permission checking dependencies and decorators for FastAPI
"""
from typing import Callable, List, Optional
from functools import wraps
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.user import User
from ...services.auth_service import AuthorizationService
from ...services.activity_service import ActivityService
from .auth import get_current_active_user


def require_permission(resource: str, action: str):
    """
    Dependency to require a specific permission

    Usage:
        @router.get("/documents/", dependencies=[Depends(require_permission("document", "read"))])
        async def get_documents(...):
            ...

    Args:
        resource: Resource name (e.g., 'document', 'user')
        action: Action name (e.g., 'create', 'read', 'update', 'delete')
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        if not AuthorizationService.has_permission(
            current_user, resource, action, db
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to {action} {resource}"
            )
        return current_user

    return permission_checker


def require_any_permission(permissions: List[tuple[str, str]]):
    """
    Dependency to require any of the specified permissions

    Usage:
        @router.get(
            "/reports/",
            dependencies=[Depends(require_any_permission([
                ("report", "read"),
                ("analytics", "view")
            ]))]
        )

    Args:
        permissions: List of (resource, action) tuples
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        for resource, action in permissions:
            if AuthorizationService.has_permission(
                current_user, resource, action, db
            ):
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the required permissions"
        )

    return permission_checker


def require_role(role_code: str):
    """
    Dependency to require a specific role

    Usage:
        @router.post("/admin/", dependencies=[Depends(require_role("admin"))])

    Args:
        role_code: Role code required
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ):
        if not AuthorizationService.has_role(current_user, role_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires the '{role_code}' role"
            )
        return current_user

    return role_checker


def require_any_role(role_codes: List[str]):
    """
    Dependency to require any of the specified roles

    Usage:
        @router.post(
            "/approve/",
            dependencies=[Depends(require_any_role(["approver", "admin"]))]
        )

    Args:
        role_codes: List of role codes
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ):
        if not AuthorizationService.has_any_role(current_user, role_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of these roles: {', '.join(role_codes)}"
            )
        return current_user

    return role_checker


def require_superuser(
    current_user: User = Depends(get_current_active_user)
):
    """
    Dependency to require superuser status

    Usage:
        @router.delete("/users/{id}", dependencies=[Depends(require_superuser)])
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires superuser privileges"
        )
    return current_user


class PermissionChecker:
    """
    Class-based permission checker for more complex scenarios
    """

    def __init__(
        self,
        resource: str,
        action: str,
        check_ownership: bool = False,
        check_department: bool = False
    ):
        """
        Initialize permission checker

        Args:
            resource: Resource name
            action: Action name
            check_ownership: Check if user owns the resource
            check_department: Check if resource is in user's department
        """
        self.resource = resource
        self.action = action
        self.check_ownership = check_ownership
        self.check_department = check_department

    async def __call__(
        self,
        request: Request,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """
        Check permission

        Args:
            request: FastAPI request
            current_user: Current user
            db: Database session
        """
        # Extract resource ID from path if checking ownership
        resource_owner_id = None
        resource_department = None

        if self.check_ownership or self.check_department:
            # Try to get resource from database
            # This is a simplified example - actual implementation would
            # fetch the resource based on the resource type and ID from the path
            pass

        # Check permission
        if not AuthorizationService.has_permission(
            current_user,
            self.resource,
            self.action,
            db,
            resource_owner_id=resource_owner_id,
            resource_department=resource_department
        ):
            # Log unauthorized access attempt
            ActivityService.log_suspicious_activity(
                db=db,
                user=current_user,
                description=f"Unauthorized access attempt to {self.action} {self.resource}",
                request=request,
                metadata={
                    'resource': self.resource,
                    'action': self.action,
                    'path': str(request.url.path)
                }
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to {self.action} {self.resource}"
            )

        return current_user


def check_resource_access(resource_type: str, get_resource_func: Callable):
    """
    Decorator to check access to a specific resource

    Usage:
        @router.get("/documents/{document_id}")
        @check_resource_access("document", get_document_by_id)
        async def get_document(document_id: int, ...):
            ...

    Args:
        resource_type: Type of resource
        get_resource_func: Function to get the resource
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract necessary dependencies
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            resource_id = kwargs.get(f'{resource_type}_id')

            if not current_user or not db or not resource_id:
                return await func(*args, **kwargs)

            # Get resource
            resource = get_resource_func(db, resource_id)
            if not resource:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{resource_type.capitalize()} not found"
                )

            # Check access
            resource_owner_id = getattr(resource, 'created_by_id', None)
            resource_department = getattr(resource, 'department', None)

            has_access, reason = AuthorizationService.check_resource_access(
                current_user,
                resource_type,
                resource_id,
                'read',  # Default action
                db
            )

            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=reason or f"Access denied to {resource_type}"
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


# Middleware for logging all API requests
class ActivityLoggingMiddleware:
    """
    Middleware to log all API requests to user activity log
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next):
        # Skip logging for health checks and static files
        if request.url.path in ['/health', '/docs', '/redoc', '/openapi.json']:
            return await call_next(request)

        # Process request
        response = await call_next(request)

        # Log activity (async after response)
        # Note: In production, this should be done in a background task
        # to avoid blocking the response

        return response
