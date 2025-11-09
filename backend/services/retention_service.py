"""
Document Retention Service
Manages document retention policies and lifecycle
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.models.document import (
    Document,
    DocumentRetentionPolicy,
    DocumentLevelEnum,
    DocumentTypeEnum,
    DocumentStatusEnum,
    DocumentAuditLog
)


class RetentionService:
    """Service for managing document retention and lifecycle"""

    def __init__(self, db: Session):
        self.db = db

    def create_retention_policy(
        self,
        policy_name: str,
        retention_years: int,
        retention_months: int = 0,
        document_level: Optional[DocumentLevelEnum] = None,
        document_type: Optional[DocumentTypeEnum] = None,
        category: Optional[str] = None,
        auto_archive: bool = False,
        auto_destroy: bool = False,
        require_approval_for_destruction: bool = True,
        legal_requirement: bool = False,
        regulation_reference: Optional[str] = None,
        description: Optional[str] = None,
        notes: Optional[str] = None
    ) -> dict:
        """
        Create a retention policy

        Args:
            policy_name: Name of the policy
            retention_years: Retention period in years
            retention_months: Additional months
            document_level: Applicable document level
            document_type: Applicable document type
            category: Applicable category
            auto_archive: Auto-archive after retention
            auto_destroy: Auto-destroy after retention
            require_approval_for_destruction: Require approval before destruction
            legal_requirement: Is this a legal requirement
            regulation_reference: Reference to regulation
            description: Policy description
            notes: Additional notes

        Returns:
            Created policy information
        """
        # Check if policy already exists
        existing = self.db.query(DocumentRetentionPolicy).filter(
            DocumentRetentionPolicy.policy_name == policy_name
        ).first()

        if existing:
            raise ValueError(f"Retention policy already exists: {policy_name}")

        # Create policy
        policy = DocumentRetentionPolicy(
            policy_name=policy_name,
            retention_years=retention_years,
            retention_months=retention_months,
            document_level=document_level,
            document_type=document_type,
            category=category,
            auto_archive=auto_archive,
            auto_destroy=auto_destroy,
            require_approval_for_destruction=require_approval_for_destruction,
            legal_requirement=legal_requirement,
            regulation_reference=regulation_reference,
            description=description,
            notes=notes
        )

        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)

        return {
            'status': 'success',
            'message': 'Retention policy created successfully',
            'policy_id': policy.id,
            'policy_name': policy_name
        }

    def get_applicable_policy(
        self,
        document_id: int
    ) -> Optional[dict]:
        """
        Get the applicable retention policy for a document

        Args:
            document_id: Document ID

        Returns:
            Applicable policy or None
        """
        document = self._get_document(document_id)

        # Try to find most specific policy first
        # 1. Level + Type + Category
        policy = self.db.query(DocumentRetentionPolicy).filter(
            DocumentRetentionPolicy.document_level == document.level,
            DocumentRetentionPolicy.document_type == document.document_type,
            DocumentRetentionPolicy.category == document.category
        ).first()

        # 2. Level + Type
        if not policy:
            policy = self.db.query(DocumentRetentionPolicy).filter(
                DocumentRetentionPolicy.document_level == document.level,
                DocumentRetentionPolicy.document_type == document.document_type,
                DocumentRetentionPolicy.category.is_(None)
            ).first()

        # 3. Level + Category
        if not policy:
            policy = self.db.query(DocumentRetentionPolicy).filter(
                DocumentRetentionPolicy.document_level == document.level,
                DocumentRetentionPolicy.document_type.is_(None),
                DocumentRetentionPolicy.category == document.category
            ).first()

        # 4. Level only
        if not policy:
            policy = self.db.query(DocumentRetentionPolicy).filter(
                DocumentRetentionPolicy.document_level == document.level,
                DocumentRetentionPolicy.document_type.is_(None),
                DocumentRetentionPolicy.category.is_(None)
            ).first()

        # 5. Type + Category
        if not policy:
            policy = self.db.query(DocumentRetentionPolicy).filter(
                DocumentRetentionPolicy.document_level.is_(None),
                DocumentRetentionPolicy.document_type == document.document_type,
                DocumentRetentionPolicy.category == document.category
            ).first()

        # 6. Category only
        if not policy:
            policy = self.db.query(DocumentRetentionPolicy).filter(
                DocumentRetentionPolicy.document_level.is_(None),
                DocumentRetentionPolicy.document_type.is_(None),
                DocumentRetentionPolicy.category == document.category
            ).first()

        if not policy:
            return None

        return {
            'id': policy.id,
            'policy_name': policy.policy_name,
            'retention_years': policy.retention_years,
            'retention_months': policy.retention_months,
            'auto_archive': policy.auto_archive,
            'auto_destroy': policy.auto_destroy,
            'legal_requirement': policy.legal_requirement,
            'regulation_reference': policy.regulation_reference
        }

    def calculate_destruction_date(
        self,
        document_id: int,
        from_date: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Calculate when a document should be destroyed based on retention policy

        Args:
            document_id: Document ID
            from_date: Date to calculate from (defaults to effective_date or created_at)

        Returns:
            Destruction date or None if no policy applies
        """
        document = self._get_document(document_id)
        policy = self.get_applicable_policy(document_id)

        if not policy:
            # Use document's own retention_years if no policy
            if document.retention_years > 0:
                base_date = from_date or document.effective_date or document.created_at
                return base_date + timedelta(days=365 * document.retention_years)
            return None

        # Calculate from policy
        retention_years = policy['retention_years']
        retention_months = policy.get('retention_months', 0)

        base_date = from_date or document.effective_date or document.created_at
        destruction_date = base_date + timedelta(days=365 * retention_years + 30 * retention_months)

        return destruction_date

    def apply_retention_policy(
        self,
        document_id: int,
        user_id: Optional[int] = None
    ) -> dict:
        """
        Apply retention policy to a document

        Args:
            document_id: Document ID
            user_id: User applying policy

        Returns:
            Application result
        """
        document = self._get_document(document_id)
        policy = self.get_applicable_policy(document_id)

        if not policy:
            return {
                'status': 'warning',
                'message': 'No applicable retention policy found',
                'document_id': document_id
            }

        # Calculate and set destruction date
        destruction_date = self.calculate_destruction_date(document_id)
        document.destruction_date = destruction_date

        # Update document retention years from policy
        document.retention_years = policy['retention_years']

        # Create audit log
        if user_id:
            self._create_audit_log(
                document_id=document_id,
                user_id=user_id,
                action="retention_policy_applied",
                notes=f"Applied policy: {policy['policy_name']}, Destruction date: {destruction_date}"
            )

        self.db.commit()

        return {
            'status': 'success',
            'message': 'Retention policy applied successfully',
            'policy_name': policy['policy_name'],
            'destruction_date': destruction_date.isoformat() if destruction_date else None
        }

    def get_documents_for_review(
        self,
        days_before_destruction: int = 90
    ) -> List[dict]:
        """
        Get documents approaching destruction date for review

        Args:
            days_before_destruction: Number of days before destruction to include

        Returns:
            List of documents for review
        """
        cutoff_date = datetime.now() + timedelta(days=days_before_destruction)

        documents = self.db.query(Document).filter(
            Document.destruction_date.isnot(None),
            Document.destruction_date <= cutoff_date,
            Document.is_deleted == False,
            Document.status != DocumentStatusEnum.ARCHIVED
        ).all()

        results = []
        for doc in documents:
            days_remaining = (doc.destruction_date - datetime.now()).days if doc.destruction_date else None

            results.append({
                'id': doc.id,
                'document_number': doc.document_number,
                'title': doc.title,
                'level': doc.level.value,
                'status': doc.status.value,
                'destruction_date': doc.destruction_date.isoformat() if doc.destruction_date else None,
                'days_remaining': days_remaining,
                'retention_years': doc.retention_years
            })

        return sorted(results, key=lambda x: x['days_remaining'] if x['days_remaining'] else float('inf'))

    def archive_document(
        self,
        document_id: int,
        user_id: Optional[int] = None,
        reason: Optional[str] = None
    ) -> dict:
        """
        Archive a document

        Args:
            document_id: Document ID
            user_id: User archiving document
            reason: Reason for archiving

        Returns:
            Archive result
        """
        document = self._get_document(document_id)

        # Update status
        old_status = document.status
        document.status = DocumentStatusEnum.ARCHIVED

        # Create audit log
        if user_id:
            self._create_audit_log(
                document_id=document_id,
                user_id=user_id,
                action="document_archived",
                notes=f"Archived from {old_status.value}. Reason: {reason}"
            )

        self.db.commit()

        return {
            'status': 'success',
            'message': 'Document archived successfully',
            'document_id': document_id
        }

    def destroy_document(
        self,
        document_id: int,
        user_id: int,
        approved_by: Optional[int] = None,
        reason: Optional[str] = None
    ) -> dict:
        """
        Destroy a document (soft delete with audit trail)

        Args:
            document_id: Document ID
            user_id: User destroying document
            approved_by: Approver user ID (if required)
            reason: Reason for destruction

        Returns:
            Destruction result
        """
        document = self._get_document(document_id)
        policy = self.get_applicable_policy(document_id)

        # Check if approval required
        if policy and policy.get('require_approval_for_destruction', True):
            if not approved_by:
                raise ValueError("Approval required for document destruction")

        # Mark as deleted (soft delete)
        document.is_deleted = True
        document.is_active = False

        # Create audit log
        self._create_audit_log(
            document_id=document_id,
            user_id=user_id,
            action="document_destroyed",
            notes=f"Document destroyed. Approved by: {approved_by}. Reason: {reason}"
        )

        self.db.commit()

        return {
            'status': 'success',
            'message': 'Document destroyed successfully',
            'document_id': document_id
        }

    def extend_retention(
        self,
        document_id: int,
        additional_years: int,
        user_id: Optional[int] = None,
        reason: Optional[str] = None
    ) -> dict:
        """
        Extend retention period for a document

        Args:
            document_id: Document ID
            additional_years: Years to extend
            user_id: User extending retention
            reason: Reason for extension

        Returns:
            Extension result
        """
        document = self._get_document(document_id)

        # Update retention years
        old_retention = document.retention_years
        document.retention_years += additional_years

        # Recalculate destruction date
        if document.destruction_date:
            document.destruction_date += timedelta(days=365 * additional_years)

        # Create audit log
        if user_id:
            self._create_audit_log(
                document_id=document_id,
                user_id=user_id,
                action="retention_extended",
                notes=f"Extended from {old_retention} to {document.retention_years} years. Reason: {reason}"
            )

        self.db.commit()

        return {
            'status': 'success',
            'message': 'Retention period extended successfully',
            'old_retention_years': old_retention,
            'new_retention_years': document.retention_years,
            'new_destruction_date': document.destruction_date.isoformat() if document.destruction_date else None
        }

    def get_retention_report(self) -> dict:
        """
        Generate retention report showing document distribution by retention period

        Returns:
            Retention statistics
        """
        from sqlalchemy import func

        # Count by retention years
        retention_counts = self.db.query(
            Document.retention_years,
            func.count(Document.id).label('count')
        ).filter(
            Document.is_deleted == False
        ).group_by(Document.retention_years).all()

        # Count documents approaching destruction
        approaching = len(self.get_documents_for_review(90))

        # Count archived documents
        archived_count = self.db.query(func.count(Document.id)).filter(
            Document.status == DocumentStatusEnum.ARCHIVED,
            Document.is_deleted == False
        ).scalar()

        return {
            'by_retention_period': [
                {'years': years, 'count': count}
                for years, count in retention_counts
            ],
            'approaching_destruction': approaching,
            'archived': archived_count,
            'total_policies': self.db.query(func.count(DocumentRetentionPolicy.id)).scalar()
        }

    def list_retention_policies(self) -> List[dict]:
        """List all retention policies"""
        policies = self.db.query(DocumentRetentionPolicy).all()

        return [{
            'id': p.id,
            'policy_name': p.policy_name,
            'retention_years': p.retention_years,
            'retention_months': p.retention_months,
            'document_level': p.document_level.value if p.document_level else None,
            'document_type': p.document_type.value if p.document_type else None,
            'category': p.category,
            'auto_archive': p.auto_archive,
            'auto_destroy': p.auto_destroy,
            'legal_requirement': p.legal_requirement,
            'regulation_reference': p.regulation_reference
        } for p in policies]

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
