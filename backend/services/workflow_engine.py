"""
Workflow Engine for Doer-Checker-Approver Flow
Implements state machine for form record approval workflow
"""
from sqlalchemy.orm import Session
from backend.models.form import FormRecord
from backend.models.form_workflow import (
    WorkflowTransition, WorkflowStatus, WorkflowAction,
    FormSignature, FormHistory
)
from backend.models.notification import Notification
from typing import Optional, Dict, Any
from datetime import datetime
import hashlib
import json


class WorkflowEngine:
    """Manage form record workflow state transitions"""

    def __init__(self, db: Session):
        self.db = db

        # Define allowed state transitions
        self.transitions = {
            WorkflowStatus.DRAFT: [
                (WorkflowAction.SUBMIT, WorkflowStatus.SUBMITTED),
                (WorkflowAction.CANCEL, WorkflowStatus.CANCELLED)
            ],
            WorkflowStatus.SUBMITTED: [
                (WorkflowAction.ASSIGN_CHECKER, WorkflowStatus.IN_REVIEW),
                (WorkflowAction.CANCEL, WorkflowStatus.CANCELLED)
            ],
            WorkflowStatus.IN_REVIEW: [
                (WorkflowAction.CHECKER_APPROVE, WorkflowStatus.CHECKER_APPROVED),
                (WorkflowAction.CHECKER_REJECT, WorkflowStatus.CHECKER_REJECTED),
                (WorkflowAction.REQUEST_CHANGES, WorkflowStatus.DRAFT)
            ],
            WorkflowStatus.CHECKER_APPROVED: [
                (WorkflowAction.ASSIGN_APPROVER, WorkflowStatus.APPROVER_REVIEW),
                (WorkflowAction.APPROVER_APPROVE, WorkflowStatus.COMPLETED)
            ],
            WorkflowStatus.CHECKER_REJECTED: [
                (WorkflowAction.RESUBMIT, WorkflowStatus.SUBMITTED)
            ],
            WorkflowStatus.APPROVER_REVIEW: [
                (WorkflowAction.APPROVER_APPROVE, WorkflowStatus.COMPLETED),
                (WorkflowAction.APPROVER_REJECT, WorkflowStatus.APPROVER_REJECTED),
                (WorkflowAction.REQUEST_CHANGES, WorkflowStatus.IN_REVIEW)
            ],
            WorkflowStatus.APPROVER_REJECTED: [
                (WorkflowAction.RESUBMIT, WorkflowStatus.IN_REVIEW)
            ]
        }

    def submit_record(
        self,
        record_id: int,
        user_id: int,
        comments: str = None,
        signature_data: str = None
    ) -> FormRecord:
        """Submit a record for review (Doer submits)"""
        record = self._get_record(record_id)

        # Validate current status
        if record.status != WorkflowStatus.DRAFT.value:
            raise ValueError(f"Cannot submit record in status: {record.status}")

        # Update record
        record.status = WorkflowStatus.SUBMITTED.value
        record.submitted_at = str(datetime.utcnow())
        record.doer_id = user_id

        # Create workflow transition
        self._create_transition(
            record_id=record_id,
            from_status=WorkflowStatus.DRAFT,
            to_status=WorkflowStatus.SUBMITTED,
            action=WorkflowAction.SUBMIT,
            actor_id=user_id,
            comments=comments
        )

        # Create signature if provided
        if signature_data:
            self._create_signature(
                record_id=record_id,
                user_id=user_id,
                role='doer',
                signature_data=signature_data
            )

        # Create history entry
        self._create_history(
            record_id=record_id,
            changed_by_id=user_id,
            change_type='submitted',
            comments=comments
        )

        # Send notification to potential checkers
        self._send_notification(
            record=record,
            event='on_submit',
            recipient_role='checker',
            message=f"New form record {record.record_number} submitted for review"
        )

        self.db.commit()
        self.db.refresh(record)

        return record

    def assign_checker(
        self,
        record_id: int,
        checker_id: int,
        assigned_by_id: int,
        comments: str = None
    ) -> FormRecord:
        """Assign a checker to review the record"""
        record = self._get_record(record_id)

        # Validate current status
        if record.status != WorkflowStatus.SUBMITTED.value:
            raise ValueError(f"Cannot assign checker in status: {record.status}")

        # Update record
        record.status = WorkflowStatus.IN_REVIEW.value
        record.checker_id = checker_id

        # Create workflow transition
        self._create_transition(
            record_id=record_id,
            from_status=WorkflowStatus.SUBMITTED,
            to_status=WorkflowStatus.IN_REVIEW,
            action=WorkflowAction.ASSIGN_CHECKER,
            actor_id=assigned_by_id,
            comments=comments,
            metadata={'checker_id': checker_id}
        )

        # Create history entry
        self._create_history(
            record_id=record_id,
            changed_by_id=assigned_by_id,
            change_type='checker_assigned',
            comments=comments
        )

        # Send notification to assigned checker
        self._send_notification(
            record=record,
            event='on_checker_assign',
            recipient_user_id=checker_id,
            message=f"You have been assigned to check form record {record.record_number}"
        )

        self.db.commit()
        self.db.refresh(record)

        return record

    def checker_review(
        self,
        record_id: int,
        checker_id: int,
        approved: bool,
        comments: str = None,
        signature_data: str = None
    ) -> FormRecord:
        """Checker reviews and approves/rejects the record"""
        record = self._get_record(record_id)

        # Validate checker
        if record.checker_id != checker_id:
            raise ValueError("Only assigned checker can review this record")

        # Validate current status
        if record.status != WorkflowStatus.IN_REVIEW.value:
            raise ValueError(f"Cannot review record in status: {record.status}")

        # Determine new status
        if approved:
            new_status = WorkflowStatus.CHECKER_APPROVED
            action = WorkflowAction.CHECKER_APPROVE
            change_type = 'checker_approved'
            notification_msg = f"Form record {record.record_number} approved by checker"
        else:
            new_status = WorkflowStatus.CHECKER_REJECTED
            action = WorkflowAction.CHECKER_REJECT
            change_type = 'checker_rejected'
            notification_msg = f"Form record {record.record_number} rejected by checker"

        # Update record
        record.status = new_status.value
        record.checked_at = str(datetime.utcnow())
        record.checker_comments = comments

        # Create workflow transition
        self._create_transition(
            record_id=record_id,
            from_status=WorkflowStatus.IN_REVIEW,
            to_status=new_status,
            action=action,
            actor_id=checker_id,
            comments=comments
        )

        # Create signature if provided
        if signature_data:
            self._create_signature(
                record_id=record_id,
                user_id=checker_id,
                role='checker',
                signature_data=signature_data
            )

        # Create history entry
        self._create_history(
            record_id=record_id,
            changed_by_id=checker_id,
            change_type=change_type,
            comments=comments
        )

        # Send notification to doer
        if record.doer_id:
            self._send_notification(
                record=record,
                event='on_checker_review',
                recipient_user_id=record.doer_id,
                message=notification_msg
            )

        self.db.commit()
        self.db.refresh(record)

        return record

    def assign_approver(
        self,
        record_id: int,
        approver_id: int,
        assigned_by_id: int,
        comments: str = None
    ) -> FormRecord:
        """Assign an approver for final approval"""
        record = self._get_record(record_id)

        # Validate current status
        if record.status != WorkflowStatus.CHECKER_APPROVED.value:
            raise ValueError(f"Cannot assign approver in status: {record.status}")

        # Update record
        record.approver_id = approver_id

        # Create workflow transition
        self._create_transition(
            record_id=record_id,
            from_status=WorkflowStatus.CHECKER_APPROVED,
            to_status=WorkflowStatus.APPROVER_REVIEW,
            action=WorkflowAction.ASSIGN_APPROVER,
            actor_id=assigned_by_id,
            comments=comments,
            metadata={'approver_id': approver_id}
        )

        # Create history entry
        self._create_history(
            record_id=record_id,
            changed_by_id=assigned_by_id,
            change_type='approver_assigned',
            comments=comments
        )

        # Send notification to assigned approver
        self._send_notification(
            record=record,
            event='on_approver_assign',
            recipient_user_id=approver_id,
            message=f"You have been assigned to approve form record {record.record_number}"
        )

        self.db.commit()
        self.db.refresh(record)

        return record

    def approver_review(
        self,
        record_id: int,
        approver_id: int,
        approved: bool,
        comments: str = None,
        signature_data: str = None
    ) -> FormRecord:
        """Approver gives final approval/rejection"""
        record = self._get_record(record_id)

        # Validate approver
        if record.approver_id != approver_id:
            raise ValueError("Only assigned approver can approve this record")

        # Determine new status
        if approved:
            new_status = WorkflowStatus.COMPLETED
            action = WorkflowAction.APPROVER_APPROVE
            change_type = 'approved'
            notification_msg = f"Form record {record.record_number} has been approved"
        else:
            new_status = WorkflowStatus.APPROVER_REJECTED
            action = WorkflowAction.APPROVER_REJECT
            change_type = 'rejected'
            notification_msg = f"Form record {record.record_number} has been rejected by approver"

        # Update record
        record.status = new_status.value
        record.approved_at = str(datetime.utcnow())
        record.approver_comments = comments

        # Create workflow transition
        self._create_transition(
            record_id=record_id,
            from_status=WorkflowStatus.APPROVER_REVIEW,
            to_status=new_status,
            action=action,
            actor_id=approver_id,
            comments=comments
        )

        # Create signature if provided
        if signature_data:
            self._create_signature(
                record_id=record_id,
                user_id=approver_id,
                role='approver',
                signature_data=signature_data
            )

        # Create history entry
        self._create_history(
            record_id=record_id,
            changed_by_id=approver_id,
            change_type=change_type,
            comments=comments
        )

        # Send notification to doer and checker
        for user_id in [record.doer_id, record.checker_id]:
            if user_id:
                self._send_notification(
                    record=record,
                    event='on_approver_review',
                    recipient_user_id=user_id,
                    message=notification_msg
                )

        self.db.commit()
        self.db.refresh(record)

        return record

    def request_changes(
        self,
        record_id: int,
        user_id: int,
        comments: str,
        back_to_doer: bool = True
    ) -> FormRecord:
        """Request changes to the record"""
        record = self._get_record(record_id)

        # Determine target status
        if back_to_doer:
            new_status = WorkflowStatus.DRAFT
        else:
            new_status = WorkflowStatus.IN_REVIEW

        # Update record
        old_status = WorkflowStatus(record.status)
        record.status = new_status.value

        # Create workflow transition
        self._create_transition(
            record_id=record_id,
            from_status=old_status,
            to_status=new_status,
            action=WorkflowAction.REQUEST_CHANGES,
            actor_id=user_id,
            comments=comments
        )

        # Create history entry
        self._create_history(
            record_id=record_id,
            changed_by_id=user_id,
            change_type='changes_requested',
            comments=comments
        )

        # Send notification to doer
        if record.doer_id:
            self._send_notification(
                record=record,
                event='on_changes_requested',
                recipient_user_id=record.doer_id,
                message=f"Changes requested for form record {record.record_number}"
            )

        self.db.commit()
        self.db.refresh(record)

        return record

    def _get_record(self, record_id: int) -> FormRecord:
        """Get form record by ID"""
        record = self.db.query(FormRecord).filter(
            FormRecord.id == record_id,
            FormRecord.is_deleted == False
        ).first()

        if not record:
            raise ValueError(f"Record {record_id} not found")

        return record

    def _create_transition(
        self,
        record_id: int,
        from_status: Optional[WorkflowStatus],
        to_status: WorkflowStatus,
        action: WorkflowAction,
        actor_id: int,
        comments: str = None,
        metadata: Dict[str, Any] = None
    ) -> WorkflowTransition:
        """Create workflow transition record"""
        transition = WorkflowTransition(
            record_id=record_id,
            from_status=from_status,
            to_status=to_status,
            action=action,
            actor_id=actor_id,
            comments=comments,
            metadata=metadata,
            transition_time=datetime.utcnow()
        )

        self.db.add(transition)
        self.db.flush()

        return transition

    def _create_signature(
        self,
        record_id: int,
        user_id: int,
        role: str,
        signature_data: str,
        ip_address: str = None,
        user_agent: str = None
    ) -> FormSignature:
        """Create digital signature"""
        # Generate hash of signature data
        signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()

        signature = FormSignature(
            record_id=record_id,
            user_id=user_id,
            role=role,
            signature_data=signature_data,
            signature_hash=signature_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            signed_at=datetime.utcnow(),
            is_verified=True
        )

        self.db.add(signature)
        self.db.flush()

        return signature

    def _create_history(
        self,
        record_id: int,
        changed_by_id: int,
        change_type: str,
        comments: str = None,
        changes: Dict[str, Any] = None,
        snapshot: Dict[str, Any] = None
    ) -> FormHistory:
        """Create history entry"""
        # Get current version number
        version_number = self.db.query(FormHistory).filter(
            FormHistory.record_id == record_id
        ).count() + 1

        history = FormHistory(
            record_id=record_id,
            version_number=version_number,
            changed_by_id=changed_by_id,
            change_type=change_type,
            comments=comments,
            changes=changes,
            snapshot=snapshot,
            changed_at=datetime.utcnow()
        )

        self.db.add(history)
        self.db.flush()

        return history

    def _send_notification(
        self,
        record: FormRecord,
        event: str,
        message: str,
        recipient_role: str = None,
        recipient_user_id: int = None
    ):
        """Send notification to users"""
        if recipient_user_id:
            notification = Notification(
                user_id=recipient_user_id,
                title=f"Form Record: {record.record_number}",
                message=message,
                notification_type='info',
                category='approval',
                link=f"/forms/records/{record.id}",
                priority='normal',
                metadata={'record_id': record.id, 'event': event}
            )
            self.db.add(notification)

    def get_workflow_history(self, record_id: int) -> list:
        """Get complete workflow history for a record"""
        transitions = self.db.query(WorkflowTransition).filter(
            WorkflowTransition.record_id == record_id
        ).order_by(WorkflowTransition.transition_time.asc()).all()

        return [
            {
                'from_status': t.from_status.value if t.from_status else None,
                'to_status': t.to_status.value,
                'action': t.action.value,
                'actor_id': t.actor_id,
                'comments': t.comments,
                'transition_time': t.transition_time.isoformat(),
                'metadata': t.metadata
            }
            for t in transitions
        ]

    def get_signatures(self, record_id: int) -> list:
        """Get all signatures for a record"""
        signatures = self.db.query(FormSignature).filter(
            FormSignature.record_id == record_id
        ).order_by(FormSignature.signed_at.asc()).all()

        return [
            {
                'user_id': s.user_id,
                'role': s.role,
                'signed_at': s.signed_at.isoformat(),
                'is_verified': s.is_verified,
                'ip_address': s.ip_address
            }
            for s in signatures
        ]
