"""
Authorization and Permission Checking Service
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from ..models.user import User, Role, Permission, RoleDelegation
from ..core.database import get_db


class AuthorizationService:
    """Service for handling authorization and permission checking"""

    @staticmethod
    def get_user_permissions(user: User, db: Session) -> List[str]:
        """
        Get all permissions for a user (including from roles and delegations)

        Args:
            user: User object
            db: Database session

        Returns:
            List of permission strings in format "resource:action"
        """
        permissions = set()

        # Get permissions from user's roles
        for role in user.roles:
            if role.is_active:
                for permission in role.permissions:
                    if permission.is_active:
                        perm_str = f"{permission.resource}:{permission.action}"
                        permissions.add(perm_str)

        # Get permissions from active delegations
        delegations = db.query(RoleDelegation).filter(
            RoleDelegation.delegate_id == user.id,
            RoleDelegation.is_active == True,
            RoleDelegation.start_date <= datetime.utcnow(),
            RoleDelegation.end_date >= datetime.utcnow()
        ).all()

        for delegation in delegations:
            if delegation.scope == 'all' and delegation.role_id:
                role = db.query(Role).filter(Role.id == delegation.role_id).first()
                if role:
                    for permission in role.permissions:
                        if permission.is_active:
                            perm_str = f"{permission.resource}:{permission.action}"
                            permissions.add(perm_str)
            elif delegation.scope == 'specific_permissions' and delegation.permissions:
                for perm in delegation.permissions:
                    permissions.add(perm)

        return list(permissions)

    @staticmethod
    def has_permission(
        user: User,
        resource: str,
        action: str,
        db: Session,
        resource_owner_id: Optional[int] = None,
        resource_department: Optional[str] = None
    ) -> bool:
        """
        Check if user has permission to perform action on resource

        Args:
            user: User object
            resource: Resource name (e.g., 'document', 'user', 'project')
            action: Action name (e.g., 'create', 'read', 'update', 'delete', 'approve')
            db: Database session
            resource_owner_id: ID of resource owner (for 'own' scope)
            resource_department: Department of resource (for 'department' scope)

        Returns:
            True if user has permission
        """
        # Superusers have all permissions
        if user.is_superuser:
            return True

        # Check if user is active
        if not user.is_active:
            return False

        # Get all user permissions
        user_permissions = AuthorizationService.get_user_permissions(user, db)

        # Check for exact permission match
        required_permission = f"{resource}:{action}"
        if required_permission in user_permissions:
            # Check scope constraints
            for role in user.roles:
                for permission in role.permissions:
                    if permission.resource == resource and permission.action == action:
                        if AuthorizationService._check_permission_scope(
                            user, permission, resource_owner_id, resource_department
                        ):
                            return True

            # Check delegated permissions
            delegations = db.query(RoleDelegation).filter(
                RoleDelegation.delegate_id == user.id,
                RoleDelegation.is_active == True,
                RoleDelegation.start_date <= datetime.utcnow(),
                RoleDelegation.end_date >= datetime.utcnow()
            ).all()

            for delegation in delegations:
                if delegation.scope == 'specific_permissions':
                    if required_permission in (delegation.permissions or []):
                        return True

        # Check for wildcard permissions
        wildcard_permission = f"{resource}:*"
        if wildcard_permission in user_permissions:
            return True

        all_permission = "*:*"
        if all_permission in user_permissions:
            return True

        return False

    @staticmethod
    def _check_permission_scope(
        user: User,
        permission: Permission,
        resource_owner_id: Optional[int],
        resource_department: Optional[str]
    ) -> bool:
        """
        Check if permission scope allows access

        Args:
            user: User object
            permission: Permission object
            resource_owner_id: ID of resource owner
            resource_department: Department of resource

        Returns:
            True if scope allows access
        """
        scope = permission.scope

        if scope == 'all':
            return True

        if scope == 'own':
            return resource_owner_id == user.id

        if scope == 'department':
            return resource_department == user.department

        if scope == 'team':
            # TODO: Implement team-based access
            # For now, same as department
            return resource_department == user.department

        return False

    @staticmethod
    def has_any_permission(user: User, permissions: List[str], db: Session) -> bool:
        """
        Check if user has any of the specified permissions

        Args:
            user: User object
            permissions: List of permission strings
            db: Database session

        Returns:
            True if user has at least one permission
        """
        for perm_str in permissions:
            resource, action = perm_str.split(':')
            if AuthorizationService.has_permission(user, resource, action, db):
                return True
        return False

    @staticmethod
    def has_all_permissions(user: User, permissions: List[str], db: Session) -> bool:
        """
        Check if user has all specified permissions

        Args:
            user: User object
            permissions: List of permission strings
            db: Database session

        Returns:
            True if user has all permissions
        """
        for perm_str in permissions:
            resource, action = perm_str.split(':')
            if not AuthorizationService.has_permission(user, resource, action, db):
                return False
        return True

    @staticmethod
    def has_role(user: User, role_code: str) -> bool:
        """
        Check if user has a specific role

        Args:
            user: User object
            role_code: Role code to check

        Returns:
            True if user has the role
        """
        return any(role.code == role_code and role.is_active for role in user.roles)

    @staticmethod
    def has_any_role(user: User, role_codes: List[str]) -> bool:
        """
        Check if user has any of the specified roles

        Args:
            user: User object
            role_codes: List of role codes

        Returns:
            True if user has at least one role
        """
        return any(AuthorizationService.has_role(user, code) for code in role_codes)

    @staticmethod
    def can_access_department(user: User, department: str) -> bool:
        """
        Check if user can access resources from a specific department

        Args:
            user: User object
            department: Department name

        Returns:
            True if user can access the department
        """
        # Superusers can access all departments
        if user.is_superuser:
            return True

        # Users can access their own department
        if user.department == department:
            return True

        # Check if user has cross-department permissions
        # (could be enhanced with specific department access rules)
        return False

    @staticmethod
    def filter_by_access(
        user: User,
        query,
        model_class,
        db: Session,
        resource_name: str = None
    ):
        """
        Filter query results based on user access permissions

        Args:
            user: User object
            query: SQLAlchemy query
            model_class: Model class being queried
            db: Database session
            resource_name: Resource name for permission check

        Returns:
            Filtered query
        """
        # Superusers see everything
        if user.is_superuser:
            return query

        # Check if model has owner or department fields
        if hasattr(model_class, 'created_by_id'):
            # Users can see their own records
            query = query.filter(
                (model_class.created_by_id == user.id) |
                (model_class.department == user.department) if hasattr(model_class, 'department') else True
            )

        return query

    @staticmethod
    def get_accessible_departments(user: User, db: Session) -> List[str]:
        """
        Get list of departments user can access

        Args:
            user: User object
            db: Database session

        Returns:
            List of department names
        """
        if user.is_superuser:
            # Return all departments
            # TODO: Query actual departments from database
            return []

        # Return user's own department
        return [user.department] if user.department else []

    @staticmethod
    def check_resource_access(
        user: User,
        resource_type: str,
        resource_id: int,
        action: str,
        db: Session
    ) -> tuple[bool, Optional[str]]:
        """
        Comprehensive resource access check

        Args:
            user: User object
            resource_type: Type of resource
            resource_id: Resource ID
            action: Action to perform
            db: Database session

        Returns:
            Tuple of (has_access, reason)
        """
        # Check if user has the permission
        if not AuthorizationService.has_permission(user, resource_type, action, db):
            return False, f"User does not have permission to {action} {resource_type}"

        # Additional resource-specific checks can be added here
        # For example, document classification, project membership, etc.

        return True, None
