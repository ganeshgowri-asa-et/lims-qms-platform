"""
Document Workflow Service
Implements Doer-Checker-Approver workflow with sign-offs
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from backend.models.document import (
    Document,
    DocumentApproval,
    DocumentStatusEnum,
    ApprovalActionEnum,
    DocumentAuditLog
)
from backend.models.user import User


class WorkflowService:
    """Service for managing document approval workflow"""

    def __init__(self, db: Session):
        self.db = db

    def submit_for_review(
        self,
        document_id: int,
        doer_id: int,
        checker_id: int,
        comments: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> dict:
        """
        Submit document for review (Doer submits to Checker)

        Args:
            document_id: Document ID
            doer_id: User ID of doer
            checker_id: User ID of checker
            comments: Optional submission comments
            ip_address: IP address of submission

        Returns:
            Status and approval record
        """
        document = self._get_document(document_id)

        # Validate document status
        if document.status not in [DocumentStatusEnum.DRAFT, DocumentStatusEnum.REJECTED]:
            raise ValueError(f"Document cannot be submitted from {document.status.value} status")

        # Validate doer
        if document.doer_id and document.doer_id != doer_id:
            raise ValueError("Only the assigned doer can submit this document")

        # Update document
        document.doer_id = doer_id
        document.checker_id = checker_id
        document.status = DocumentStatusEnum.PENDING_REVIEW
        document.submitted_at = func.now()

        # Create approval record
        approval = DocumentApproval(
            document_id=document_id,
            version_number=document.version,
            approval_role="doer",
            approver_id=doer_id,
            action=ApprovalActionEnum.SUBMITTED,
            comments=comments,
            ip_address=ip_address,
            sequence_number=1
        )

        self.db.add(approval)

        # Create audit log
        self._create_audit_log(
            document_id=document_id,
            user_id=doer_id,
            action="submitted_for_review",
            ip_address=ip_address,
            notes=f"Submitted to checker (User ID: {checker_id})"
        )

        self.db.commit()

        return {
            'status': 'success',
            'message': 'Document submitted for review',
            'document_status': document.status.value,
            'approval_id': approval.id
        }

    def review_document(
        self,
        document_id: int,
        checker_id: int,
        action: str,  # 'approve' or 'reject' or 'request_revision'
        approver_id: Optional[int] = None,
        comments: Optional[str] = None,
        ip_address: Optional[str] = None,
        signature: Optional[str] = None
    ) -> dict:
        """
        Review document (Checker reviews and approves/rejects)

        Args:
            document_id: Document ID
            checker_id: User ID of checker
            action: 'approve', 'reject', or 'request_revision'
            approver_id: User ID of approver (required if approving)
            comments: Review comments
            ip_address: IP address
            signature: Digital signature

        Returns:
            Status and approval record
        """
        document = self._get_document(document_id)

        # Validate document status
        if document.status != DocumentStatusEnum.PENDING_REVIEW:
            raise ValueError(f"Document is not pending review (current status: {document.status.value})")

        # Validate checker
        if document.checker_id != checker_id:
            raise ValueError("Only the assigned checker can review this document")

        # Process based on action
        if action == 'approve':
            if not approver_id:
                raise ValueError("Approver ID is required when approving")

            document.status = DocumentStatusEnum.REVIEW_APPROVED
            document.approver_id = approver_id
            document.reviewed_at = func.now()
            approval_action = ApprovalActionEnum.REVIEWED

        elif action == 'reject':
            document.status = DocumentStatusEnum.REJECTED
            approval_action = ApprovalActionEnum.REJECTED

        elif action == 'request_revision':
            document.status = DocumentStatusEnum.DRAFT
            approval_action = ApprovalActionEnum.REVISION_REQUESTED

        else:
            raise ValueError(f"Invalid action: {action}")

        # Create approval record
        approval = DocumentApproval(
            document_id=document_id,
            version_number=document.version,
            approval_role="checker",
            approver_id=checker_id,
            action=approval_action,
            comments=comments,
            ip_address=ip_address,
            signature=signature,
            sequence_number=2
        )

        self.db.add(approval)

        # Create audit log
        self._create_audit_log(
            document_id=document_id,
            user_id=checker_id,
            action=f"review_{action}",
            ip_address=ip_address,
            notes=comments
        )

        self.db.commit()

        return {
            'status': 'success',
            'message': f'Document {action}ed by checker',
            'document_status': document.status.value,
            'approval_id': approval.id
        }

    def approve_document(
        self,
        document_id: int,
        approver_id: int,
        action: str,  # 'approve' or 'reject'
        comments: Optional[str] = None,
        ip_address: Optional[str] = None,
        signature: Optional[str] = None
    ) -> dict:
        """
        Final approval of document (Approver approves/rejects)

        Args:
            document_id: Document ID
            approver_id: User ID of approver
            action: 'approve' or 'reject'
            comments: Approval comments
            ip_address: IP address
            signature: Digital signature

        Returns:
            Status and approval record
        """
        document = self._get_document(document_id)

        # Validate document status
        if document.status != DocumentStatusEnum.REVIEW_APPROVED:
            raise ValueError(f"Document is not ready for approval (current status: {document.status.value})")

        # Validate approver
        if document.approver_id != approver_id:
            raise ValueError("Only the assigned approver can approve this document")

        # Process based on action
        if action == 'approve':
            document.status = DocumentStatusEnum.APPROVED
            document.approved_at = func.now()
            document.effective_date = func.now()
            approval_action = ApprovalActionEnum.APPROVED

            # Set next review date (default: 1 year)
            from datetime import timedelta
            document.next_review_date = datetime.now() + timedelta(days=365)

        elif action == 'reject':
            document.status = DocumentStatusEnum.REJECTED
            approval_action = ApprovalActionEnum.REJECTED

        else:
            raise ValueError(f"Invalid action: {action}")

        # Create approval record
        approval = DocumentApproval(
            document_id=document_id,
            version_number=document.version,
            approval_role="approver",
            approver_id=approver_id,
            action=approval_action,
            comments=comments,
            ip_address=ip_address,
            signature=signature,
            sequence_number=3
        )

        self.db.add(approval)

        # Create audit log
        self._create_audit_log(
            document_id=document_id,
            user_id=approver_id,
            action=f"final_{action}",
            ip_address=ip_address,
            notes=comments
        )

        self.db.commit()

        return {
            'status': 'success',
            'message': f'Document {action}ed',
            'document_status': document.status.value,
            'approval_id': approval.id
        }

    def withdraw_document(
        self,
        document_id: int,
        user_id: int,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> dict:
        """Withdraw document from workflow"""
        document = self._get_document(document_id)

        # Only doer can withdraw
        if document.doer_id != user_id:
            raise ValueError("Only the document doer can withdraw the document")

        # Can only withdraw if in review process
        if document.status not in [DocumentStatusEnum.PENDING_REVIEW, DocumentStatusEnum.REVIEW_APPROVED]:
            raise ValueError(f"Document cannot be withdrawn from {document.status.value} status")

        # Update document
        old_status = document.status
        document.status = DocumentStatusEnum.DRAFT

        # Create approval record
        approval = DocumentApproval(
            document_id=document_id,
            version_number=document.version,
            approval_role="doer",
            approver_id=user_id,
            action=ApprovalActionEnum.WITHDRAWN,
            comments=reason,
            ip_address=ip_address,
            sequence_number=self._get_next_sequence(document_id)
        )

        self.db.add(approval)

        # Create audit log
        self._create_audit_log(
            document_id=document_id,
            user_id=user_id,
            action="withdrawn",
            ip_address=ip_address,
            notes=f"Withdrawn from {old_status.value}. Reason: {reason}"
        )

        self.db.commit()

        return {
            'status': 'success',
            'message': 'Document withdrawn',
            'document_status': document.status.value
        }

    def get_approval_history(self, document_id: int) -> List[dict]:
        """Get complete approval history for a document"""
        approvals = self.db.query(DocumentApproval).filter(
            DocumentApproval.document_id == document_id
        ).order_by(DocumentApproval.sequence_number.asc()).all()

        history = []
        for approval in approvals:
            # Get approver details
            approver = self.db.query(User).filter(User.id == approval.approver_id).first()

            history.append({
                'id': approval.id,
                'version': approval.version_number,
                'role': approval.approval_role,
                'approver_name': approver.full_name if approver else 'Unknown',
                'approver_email': approver.email if approver else None,
                'action': approval.action.value,
                'action_date': approval.action_date.isoformat() if approval.action_date else None,
                'comments': approval.comments,
                'sequence': approval.sequence_number,
                'has_signature': bool(approval.signature)
            })

        return history

    def get_pending_approvals(self, user_id: int, role: str = None) -> List[dict]:
        """
        Get documents pending approval for a user

        Args:
            user_id: User ID
            role: Filter by role ('checker' or 'approver')

        Returns:
            List of pending documents
        """
        query = self.db.query(Document).filter(Document.is_deleted == False)

        if role == 'checker':
            query = query.filter(
                Document.checker_id == user_id,
                Document.status == DocumentStatusEnum.PENDING_REVIEW
            )
        elif role == 'approver':
            query = query.filter(
                Document.approver_id == user_id,
                Document.status == DocumentStatusEnum.REVIEW_APPROVED
            )
        else:
            # Get all pending for user (as checker or approver)
            query = query.filter(
                ((Document.checker_id == user_id) & (Document.status == DocumentStatusEnum.PENDING_REVIEW)) |
                ((Document.approver_id == user_id) & (Document.status == DocumentStatusEnum.REVIEW_APPROVED))
            )

        documents = query.all()

        result = []
        for doc in documents:
            # Get doer details
            doer = self.db.query(User).filter(User.id == doc.doer_id).first()

            result.append({
                'id': doc.id,
                'document_number': doc.document_number,
                'title': doc.title,
                'level': doc.level.value,
                'status': doc.status.value,
                'version': doc.version,
                'submitted_at': doc.submitted_at.isoformat() if doc.submitted_at else None,
                'doer_name': doer.full_name if doer else 'Unknown',
                'pending_role': 'checker' if doc.status == DocumentStatusEnum.PENDING_REVIEW else 'approver'
            })

        return result

    def reassign_workflow(
        self,
        document_id: int,
        admin_user_id: int,
        new_doer_id: Optional[int] = None,
        new_checker_id: Optional[int] = None,
        new_approver_id: Optional[int] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> dict:
        """Reassign workflow participants (admin function)"""
        document = self._get_document(document_id)

        changes = []
        if new_doer_id and new_doer_id != document.doer_id:
            document.doer_id = new_doer_id
            changes.append(f"Doer reassigned to User ID: {new_doer_id}")

        if new_checker_id and new_checker_id != document.checker_id:
            document.checker_id = new_checker_id
            changes.append(f"Checker reassigned to User ID: {new_checker_id}")

        if new_approver_id and new_approver_id != document.approver_id:
            document.approver_id = new_approver_id
            changes.append(f"Approver reassigned to User ID: {new_approver_id}")

        if changes:
            # Create audit log
            self._create_audit_log(
                document_id=document_id,
                user_id=admin_user_id,
                action="workflow_reassigned",
                ip_address=ip_address,
                notes=f"{', '.join(changes)}. Reason: {reason}"
            )

            self.db.commit()

        return {
            'status': 'success',
            'message': 'Workflow reassigned',
            'changes': changes
        }

    def _get_document(self, document_id: int) -> Document:
        """Get document or raise error"""
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.is_deleted == False
        ).first()

        if not document:
            raise ValueError(f"Document not found: {document_id}")

        return document

    def _get_next_sequence(self, document_id: int) -> int:
        """Get next sequence number for approval"""
        max_seq = self.db.query(func.max(DocumentApproval.sequence_number)).filter(
            DocumentApproval.document_id == document_id
        ).scalar()

        return (max_seq or 0) + 1

    def _create_audit_log(
        self,
        document_id: int,
        user_id: int,
        action: str,
        ip_address: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """Create audit log entry"""
        audit = DocumentAuditLog(
            document_id=document_id,
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            notes=notes
        )
        self.db.add(audit)

    def get_workflow_status(self, document_id: int) -> dict:
        """Get current workflow status and participants"""
        document = self._get_document(document_id)

        # Get participant details
        doer = self.db.query(User).filter(User.id == document.doer_id).first() if document.doer_id else None
        checker = self.db.query(User).filter(User.id == document.checker_id).first() if document.checker_id else None
        approver = self.db.query(User).filter(User.id == document.approver_id).first() if document.approver_id else None

        return {
            'document_id': document.id,
            'document_number': document.document_number,
            'status': document.status.value,
            'version': document.version,
            'doer': {
                'id': doer.id if doer else None,
                'name': doer.full_name if doer else None,
                'email': doer.email if doer else None
            } if doer else None,
            'checker': {
                'id': checker.id if checker else None,
                'name': checker.full_name if checker else None,
                'email': checker.email if checker else None
            } if checker else None,
            'approver': {
                'id': approver.id if approver else None,
                'name': approver.full_name if approver else None,
                'email': approver.email if approver else None
            } if approver else None,
            'submitted_at': document.submitted_at.isoformat() if document.submitted_at else None,
            'reviewed_at': document.reviewed_at.isoformat() if document.reviewed_at else None,
            'approved_at': document.approved_at.isoformat() if document.approved_at else None,
            'effective_date': document.effective_date.isoformat() if document.effective_date else None,
            'next_review_date': document.next_review_date.isoformat() if document.next_review_date else None
        }
