"""
Access Control Service
Manages document access permissions and access control
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.models.document import Document, DocumentAccess, DocumentAuditLog
from backend.models.user import User


class AccessControlService:
    """Service for managing document access control"""

    def __init__(self, db: Session):
        self.db = db

    def grant_access(
        self,
        document_id: int,
        user_id: Optional[int] = None,
        role_id: Optional[int] = None,
        department_id: Optional[int] = None,
        can_view: bool = True,
        can_edit: bool = False,
        can_review: bool = False,
        can_approve: bool = False,
        can_delete: bool = False,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None,
        granted_by: Optional[int] = None
    ) -> dict:
        """
        Grant access to a document

        Args:
            document_id: Document ID
            user_id: User ID (for user-based access)
            role_id: Role ID (for role-based access)
            department_id: Department ID (for department-based access)
            can_view: View permission
            can_edit: Edit permission
            can_review: Review permission
            can_approve: Approve permission
            can_delete: Delete permission
            valid_from: Access valid from date
            valid_until: Access valid until date
            granted_by: User ID who granted access

        Returns:
            Access grant information
        """
        # Validate document exists
        document = self._get_document(document_id)

        # At least one of user_id, role_id, or department_id must be provided
        if not any([user_id, role_id, department_id]):
            raise ValueError("At least one of user_id, role_id, or department_id must be provided")

        # Check if access already exists
        existing = self.db.query(DocumentAccess).filter(
            DocumentAccess.document_id == document_id,
            DocumentAccess.user_id == user_id,
            DocumentAccess.role_id == role_id,
            DocumentAccess.department_id == department_id
        ).first()

        if existing:
            raise ValueError("Access already exists for this user/role/department")

        # Create access record
        access = DocumentAccess(
            document_id=document_id,
            user_id=user_id,
            role_id=role_id,
            department_id=department_id,
            can_view=can_view,
            can_edit=can_edit,
            can_review=can_review,
            can_approve=can_approve,
            can_delete=can_delete,
            valid_from=valid_from or datetime.now(),
            valid_until=valid_until
        )

        self.db.add(access)

        # Create audit log
        if granted_by:
            self._create_audit_log(
                document_id=document_id,
                user_id=granted_by,
                action="access_granted",
                notes=f"Access granted to user_id={user_id}, role_id={role_id}, dept_id={department_id}"
            )

        self.db.commit()
        self.db.refresh(access)

        return {
            'status': 'success',
            'message': 'Access granted successfully',
            'access_id': access.id
        }

    def revoke_access(
        self,
        access_id: int,
        revoked_by: Optional[int] = None
    ) -> dict:
        """Revoke document access"""
        access = self.db.query(DocumentAccess).filter(
            DocumentAccess.id == access_id
        ).first()

        if not access:
            raise ValueError(f"Access record not found: {access_id}")

        # Create audit log before deleting
        if revoked_by:
            self._create_audit_log(
                document_id=access.document_id,
                user_id=revoked_by,
                action="access_revoked",
                notes=f"Access revoked for user_id={access.user_id}, role_id={access.role_id}"
            )

        self.db.delete(access)
        self.db.commit()

        return {
            'status': 'success',
            'message': 'Access revoked successfully'
        }

    def update_access(
        self,
        access_id: int,
        can_view: Optional[bool] = None,
        can_edit: Optional[bool] = None,
        can_review: Optional[bool] = None,
        can_approve: Optional[bool] = None,
        can_delete: Optional[bool] = None,
        valid_until: Optional[datetime] = None,
        updated_by: Optional[int] = None
    ) -> dict:
        """Update access permissions"""
        access = self.db.query(DocumentAccess).filter(
            DocumentAccess.id == access_id
        ).first()

        if not access:
            raise ValueError(f"Access record not found: {access_id}")

        # Update permissions
        if can_view is not None:
            access.can_view = can_view
        if can_edit is not None:
            access.can_edit = can_edit
        if can_review is not None:
            access.can_review = can_review
        if can_approve is not None:
            access.can_approve = can_approve
        if can_delete is not None:
            access.can_delete = can_delete
        if valid_until is not None:
            access.valid_until = valid_until

        # Create audit log
        if updated_by:
            self._create_audit_log(
                document_id=access.document_id,
                user_id=updated_by,
                action="access_updated",
                notes=f"Access permissions updated for access_id={access_id}"
            )

        self.db.commit()

        return {
            'status': 'success',
            'message': 'Access updated successfully'
        }

    def check_permission(
        self,
        document_id: int,
        user_id: int,
        permission: str  # 'view', 'edit', 'review', 'approve', 'delete'
    ) -> bool:
        """
        Check if user has specific permission for document

        Args:
            document_id: Document ID
            user_id: User ID
            permission: Permission to check

        Returns:
            True if user has permission, False otherwise
        """
        document = self._get_document(document_id)

        # Document owner has all permissions
        if document.document_owner_id == user_id:
            return True

        # Creator has view and edit permissions
        if document.created_by_id == user_id and permission in ['view', 'edit']:
            return True

        # Check assigned roles
        if permission == 'edit' and document.doer_id == user_id:
            return True
        if permission == 'review' and document.checker_id == user_id:
            return True
        if permission == 'approve' and document.approver_id == user_id:
            return True

        # Check access control records
        access_records = self.db.query(DocumentAccess).filter(
            DocumentAccess.document_id == document_id,
            DocumentAccess.user_id == user_id
        ).all()

        current_time = datetime.now()

        for access in access_records:
            # Check validity period
            if access.valid_from and access.valid_from > current_time:
                continue
            if access.valid_until and access.valid_until < current_time:
                continue

            # Check permission
            if permission == 'view' and access.can_view:
                return True
            elif permission == 'edit' and access.can_edit:
                return True
            elif permission == 'review' and access.can_review:
                return True
            elif permission == 'approve' and access.can_approve:
                return True
            elif permission == 'delete' and access.can_delete:
                return True

        # Check role-based and department-based access
        # TODO: Implement role and department checks when user model is extended

        return False

    def get_document_access_list(self, document_id: int) -> List[dict]:
        """Get all access records for a document"""
        access_records = self.db.query(DocumentAccess).filter(
            DocumentAccess.document_id == document_id
        ).all()

        results = []
        for access in access_records:
            user = None
            if access.user_id:
                user = self.db.query(User).filter(User.id == access.user_id).first()

            results.append({
                'id': access.id,
                'user_id': access.user_id,
                'user_name': user.full_name if user else None,
                'user_email': user.email if user else None,
                'role_id': access.role_id,
                'department_id': access.department_id,
                'permissions': {
                    'view': access.can_view,
                    'edit': access.can_edit,
                    'review': access.can_review,
                    'approve': access.can_approve,
                    'delete': access.can_delete
                },
                'valid_from': access.valid_from.isoformat() if access.valid_from else None,
                'valid_until': access.valid_until.isoformat() if access.valid_until else None,
                'is_active': self._is_access_active(access)
            })

        return results

    def get_user_accessible_documents(
        self,
        user_id: int,
        permission: str = 'view',
        limit: int = 100
    ) -> List[dict]:
        """Get all documents accessible by a user"""
        # Get documents where user has explicit access
        access_records = self.db.query(DocumentAccess).filter(
            DocumentAccess.user_id == user_id
        ).all()

        document_ids = []
        current_time = datetime.now()

        for access in access_records:
            # Check validity
            if access.valid_from and access.valid_from > current_time:
                continue
            if access.valid_until and access.valid_until < current_time:
                continue

            # Check permission
            has_permission = False
            if permission == 'view' and access.can_view:
                has_permission = True
            elif permission == 'edit' and access.can_edit:
                has_permission = True
            elif permission == 'review' and access.can_review:
                has_permission = True
            elif permission == 'approve' and access.can_approve:
                has_permission = True
            elif permission == 'delete' and access.can_delete:
                has_permission = True

            if has_permission:
                document_ids.append(access.document_id)

        # Get document details
        documents = self.db.query(Document).filter(
            Document.id.in_(document_ids),
            Document.is_deleted == False
        ).limit(limit).all()

        return [{
            'id': doc.id,
            'document_number': doc.document_number,
            'title': doc.title,
            'level': doc.level.value,
            'status': doc.status.value,
            'is_confidential': doc.is_confidential
        } for doc in documents]

    def bulk_grant_access(
        self,
        document_id: int,
        user_ids: List[int],
        permissions: dict,
        granted_by: Optional[int] = None
    ) -> dict:
        """Grant access to multiple users at once"""
        granted = 0
        errors = []

        for user_id in user_ids:
            try:
                self.grant_access(
                    document_id=document_id,
                    user_id=user_id,
                    can_view=permissions.get('view', True),
                    can_edit=permissions.get('edit', False),
                    can_review=permissions.get('review', False),
                    can_approve=permissions.get('approve', False),
                    can_delete=permissions.get('delete', False),
                    granted_by=granted_by
                )
                granted += 1
            except Exception as e:
                errors.append({
                    'user_id': user_id,
                    'error': str(e)
                })

        return {
            'status': 'success' if granted > 0 else 'error',
            'granted': granted,
            'errors': errors,
            'total': len(user_ids)
        }

    def set_document_access_level(
        self,
        document_id: int,
        access_level: str,  # 'public', 'internal', 'confidential', 'restricted'
        is_confidential: bool = False,
        is_controlled: bool = True,
        updated_by: Optional[int] = None
    ) -> dict:
        """Set document access level"""
        document = self._get_document(document_id)

        document.access_level = access_level
        document.is_confidential = is_confidential
        document.is_controlled = is_controlled

        # Create audit log
        if updated_by:
            self._create_audit_log(
                document_id=document_id,
                user_id=updated_by,
                action="access_level_changed",
                notes=f"Access level changed to {access_level}"
            )

        self.db.commit()

        return {
            'status': 'success',
            'message': 'Document access level updated',
            'access_level': access_level
        }

    def _is_access_active(self, access: DocumentAccess) -> bool:
        """Check if access record is currently active"""
        current_time = datetime.now()

        if access.valid_from and access.valid_from > current_time:
            return False
        if access.valid_until and access.valid_until < current_time:
            return False

        return True

    def _get_document(self, document_id: int) -> Document:
        """Get document or raise error"""
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.is_deleted == False
        ).first()

        if not document:
            raise ValueError(f"Document not found: {document_id}")

        return document

    def _create_audit_log(
        self,
        document_id: int,
        user_id: int,
        action: str,
        notes: Optional[str] = None
    ):
        """Create audit log entry"""
        audit = DocumentAuditLog(
            document_id=document_id,
            user_id=user_id,
            action=action,
            notes=notes
        )
        self.db.add(audit)
