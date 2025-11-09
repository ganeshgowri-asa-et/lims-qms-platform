"""
Workflow Service - Doer-Checker-Approver workflow management
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import (
    FormRecord, FormWorkflowEvent, FormComment, RecordStatusEnum,
    WorkflowActionEnum, User, RecordApprovalMatrix, RecordVersionHistory
)


class WorkflowService:
    """Service for managing form record workflow"""

    def __init__(self, db: Session):
        self.db = db

    def submit_record(
        self,
        record_id: int,
        user_id: int,
        comments: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """Submit draft record for review"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record:
            return False, "Record not found"

        if record.status != RecordStatusEnum.DRAFT:
            return False, f"Cannot submit record with status: {record.status.value}"

        # Check if user is the doer
        if record.doer_id and record.doer_id != user_id:
            return False, "Only the doer can submit this record"

        # Update record status
        old_status = record.status
        record.status = RecordStatusEnum.SUBMITTED
        record.submitted_at = datetime.utcnow().isoformat()

        # Auto-assign checker if not assigned
        if not record.checker_id:
            checker = self._get_next_approver(record, 2)  # Level 2 = checker
            if checker:
                record.checker_id = checker.id

        # Create workflow event
        event = FormWorkflowEvent(
            record_id=record_id,
            action=WorkflowActionEnum.SUBMIT,
            from_status=old_status,
            to_status=record.status,
            actor_id=user_id,
            comments=comments,
            metadata=metadata
        )
        self.db.add(event)

        # Save version history
        self._save_version_history(record, user_id, "submitted", "Record submitted for review")

        self.db.commit()

        return True, "Record submitted successfully"

    def review_record(
        self,
        record_id: int,
        user_id: int,
        action: str,  # 'approve' or 'request_revision' or 'reject'
        comments: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """Checker reviews the record"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record:
            return False, "Record not found"

        if record.status != RecordStatusEnum.SUBMITTED:
            return False, f"Cannot review record with status: {record.status.value}"

        # Check if user is the checker
        if record.checker_id and record.checker_id != user_id:
            return False, "Only the assigned checker can review this record"

        old_status = record.status

        if action == "approve":
            record.status = RecordStatusEnum.UNDER_REVIEW
            record.checked_at = datetime.utcnow().isoformat()
            record.checker_comments = comments

            # Auto-assign approver if not assigned
            if not record.approver_id:
                approver = self._get_next_approver(record, 3)  # Level 3 = approver
                if approver:
                    record.approver_id = approver.id

            workflow_action = WorkflowActionEnum.REVIEW
            message = "Record reviewed and sent for approval"

        elif action == "request_revision":
            record.status = RecordStatusEnum.REVISION_REQUIRED
            record.checker_comments = comments
            workflow_action = WorkflowActionEnum.REQUEST_REVISION
            message = "Revision requested"

        elif action == "reject":
            record.status = RecordStatusEnum.REJECTED
            record.rejected_at = datetime.utcnow().isoformat()
            record.rejection_reason = comments
            workflow_action = WorkflowActionEnum.REJECT
            message = "Record rejected"

        else:
            return False, "Invalid action"

        # Create workflow event
        event = FormWorkflowEvent(
            record_id=record_id,
            action=workflow_action,
            from_status=old_status,
            to_status=record.status,
            actor_id=user_id,
            comments=comments,
            metadata=metadata
        )
        self.db.add(event)

        # Save version history
        self._save_version_history(record, user_id, action, comments or message)

        self.db.commit()

        return True, message

    def approve_record(
        self,
        record_id: int,
        user_id: int,
        action: str,  # 'approve' or 'request_revision' or 'reject'
        comments: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """Approver approves the record"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record:
            return False, "Record not found"

        if record.status != RecordStatusEnum.UNDER_REVIEW:
            return False, f"Cannot approve record with status: {record.status.value}"

        # Check if user is the approver
        if record.approver_id and record.approver_id != user_id:
            return False, "Only the assigned approver can approve this record"

        old_status = record.status

        if action == "approve":
            record.status = RecordStatusEnum.APPROVED
            record.approved_at = datetime.utcnow().isoformat()
            record.approver_comments = comments
            workflow_action = WorkflowActionEnum.APPROVE
            message = "Record approved successfully"

        elif action == "request_revision":
            record.status = RecordStatusEnum.REVISION_REQUIRED
            record.approver_comments = comments
            workflow_action = WorkflowActionEnum.REQUEST_REVISION
            message = "Revision requested"

        elif action == "reject":
            record.status = RecordStatusEnum.REJECTED
            record.rejected_at = datetime.utcnow().isoformat()
            record.rejection_reason = comments
            workflow_action = WorkflowActionEnum.REJECT
            message = "Record rejected"

        else:
            return False, "Invalid action"

        # Create workflow event
        event = FormWorkflowEvent(
            record_id=record_id,
            action=workflow_action,
            from_status=old_status,
            to_status=record.status,
            actor_id=user_id,
            comments=comments,
            metadata=metadata
        )
        self.db.add(event)

        # Save version history
        self._save_version_history(record, user_id, action, comments or message)

        self.db.commit()

        return True, message

    def revise_record(
        self,
        record_id: int,
        user_id: int,
        new_values: Dict,
        comments: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Doer revises the record after revision request"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record:
            return False, "Record not found"

        if record.status != RecordStatusEnum.REVISION_REQUIRED:
            return False, f"Cannot revise record with status: {record.status.value}"

        # Check if user is the doer
        if record.doer_id and record.doer_id != user_id:
            return False, "Only the doer can revise this record"

        old_status = record.status
        record.status = RecordStatusEnum.DRAFT
        record.revision_number += 1
        record.last_modified_at = datetime.utcnow().isoformat()

        # Clear previous review/approval
        record.checked_at = None
        record.approved_at = None
        record.rejected_at = None

        # Create workflow event
        event = FormWorkflowEvent(
            record_id=record_id,
            action=WorkflowActionEnum.REVISE,
            from_status=old_status,
            to_status=record.status,
            actor_id=user_id,
            comments=comments,
            metadata={"revision_number": record.revision_number}
        )
        self.db.add(event)

        # Save version history
        self._save_version_history(
            record,
            user_id,
            "revised",
            f"Record revised (Revision {record.revision_number})"
        )

        self.db.commit()

        return True, "Record moved to draft for revision"

    def cancel_record(
        self,
        record_id: int,
        user_id: int,
        reason: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Cancel a record"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record:
            return False, "Record not found"

        if record.status == RecordStatusEnum.APPROVED:
            return False, "Cannot cancel approved record"

        old_status = record.status
        record.status = RecordStatusEnum.CANCELLED

        # Create workflow event
        event = FormWorkflowEvent(
            record_id=record_id,
            action=WorkflowActionEnum.CANCEL,
            from_status=old_status,
            to_status=record.status,
            actor_id=user_id,
            comments=reason
        )
        self.db.add(event)

        # Save version history
        self._save_version_history(record, user_id, "cancelled", reason or "Record cancelled")

        self.db.commit()

        return True, "Record cancelled"

    def get_workflow_history(self, record_id: int) -> List[Dict]:
        """Get workflow history for a record"""
        events = self.db.query(FormWorkflowEvent).filter_by(
            record_id=record_id
        ).order_by(FormWorkflowEvent.created_at).all()

        history = []
        for event in events:
            actor = self.db.query(User).filter_by(id=event.actor_id).first()
            history.append({
                "id": event.id,
                "action": event.action.value,
                "from_status": event.from_status.value if event.from_status else None,
                "to_status": event.to_status.value,
                "actor": {
                    "id": actor.id,
                    "username": actor.username,
                    "full_name": actor.full_name
                } if actor else None,
                "comments": event.comments,
                "timestamp": event.created_at,
                "metadata": event.metadata
            })

        return history

    def add_comment(
        self,
        record_id: int,
        user_id: int,
        content: str,
        field_id: Optional[int] = None,
        comment_type: str = "general",
        parent_comment_id: Optional[int] = None
    ) -> FormComment:
        """Add comment to record"""
        comment = FormComment(
            record_id=record_id,
            field_id=field_id,
            user_id=user_id,
            comment_type=comment_type,
            content=content,
            parent_comment_id=parent_comment_id
        )
        self.db.add(comment)
        self.db.commit()
        return comment

    def get_comments(self, record_id: int) -> List[Dict]:
        """Get all comments for a record"""
        comments = self.db.query(FormComment).filter_by(
            record_id=record_id
        ).order_by(FormComment.created_at).all()

        result = []
        for comment in comments:
            user = self.db.query(User).filter_by(id=comment.user_id).first()
            result.append({
                "id": comment.id,
                "content": comment.content,
                "comment_type": comment.comment_type,
                "field_id": comment.field_id,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name
                } if user else None,
                "created_at": comment.created_at,
                "is_resolved": comment.is_resolved,
                "parent_comment_id": comment.parent_comment_id
            })

        return result

    def resolve_comment(self, comment_id: int, user_id: int) -> Tuple[bool, str]:
        """Mark comment as resolved"""
        comment = self.db.query(FormComment).filter_by(id=comment_id).first()
        if not comment:
            return False, "Comment not found"

        comment.is_resolved = True
        comment.resolved_by_id = user_id
        comment.resolved_at = datetime.utcnow().isoformat()
        self.db.commit()

        return True, "Comment resolved"

    def get_pending_approvals(self, user_id: int) -> List[Dict]:
        """Get records pending approval for a user"""
        # Records where user is checker and status is SUBMITTED
        as_checker = self.db.query(FormRecord).filter_by(
            checker_id=user_id,
            status=RecordStatusEnum.SUBMITTED
        ).all()

        # Records where user is approver and status is UNDER_REVIEW
        as_approver = self.db.query(FormRecord).filter_by(
            approver_id=user_id,
            status=RecordStatusEnum.UNDER_REVIEW
        ).all()

        result = []

        for record in as_checker:
            result.append({
                "record_id": record.id,
                "record_number": record.record_number,
                "title": record.title,
                "status": record.status.value,
                "role": "checker",
                "submitted_at": record.submitted_at,
                "template_id": record.template_id
            })

        for record in as_approver:
            result.append({
                "record_id": record.id,
                "record_number": record.record_number,
                "title": record.title,
                "status": record.status.value,
                "role": "approver",
                "checked_at": record.checked_at,
                "template_id": record.template_id
            })

        return result

    def _get_next_approver(self, record: FormRecord, level: int) -> Optional[User]:
        """Get next approver based on approval matrix"""
        matrix = self.db.query(RecordApprovalMatrix).filter_by(
            template_id=record.template_id,
            approval_level=level,
            is_required=True
        ).first()

        if not matrix:
            return None

        # If specific user is defined
        if matrix.user_id:
            return self.db.query(User).filter_by(id=matrix.user_id).first()

        # If role-based, find user with that role
        if matrix.role_id:
            # This would require querying users with that role
            # For now, return None
            return None

        # Department-based assignment could be implemented here
        return None

    def _save_version_history(
        self,
        record: FormRecord,
        user_id: int,
        change_type: str,
        change_summary: str
    ) -> None:
        """Save version history"""
        # Get current version number
        last_version = self.db.query(RecordVersionHistory).filter_by(
            record_id=record.id
        ).order_by(RecordVersionHistory.version_number.desc()).first()

        version_number = 1
        if last_version:
            version_number = last_version.version_number + 1

        version = RecordVersionHistory(
            record_id=record.id,
            version_number=version_number,
            changed_by_id=user_id,
            change_type=change_type,
            change_summary=change_summary,
            status_before=None,  # Would need to track this
            status_after=record.status.value,
            field_changes={},  # Would need to track field-level changes
            snapshot_data={}  # Could snapshot entire record data
        )
        self.db.add(version)

    def check_workflow_permissions(
        self,
        record_id: int,
        user_id: int,
        action: str
    ) -> Tuple[bool, str]:
        """Check if user has permission to perform workflow action"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record:
            return False, "Record not found"

        if action == "submit":
            if record.doer_id and record.doer_id != user_id:
                return False, "Only the doer can submit"
            if record.status != RecordStatusEnum.DRAFT:
                return False, f"Cannot submit from status: {record.status.value}"

        elif action == "review":
            if record.checker_id and record.checker_id != user_id:
                return False, "Only the assigned checker can review"
            if record.status != RecordStatusEnum.SUBMITTED:
                return False, f"Cannot review from status: {record.status.value}"

        elif action == "approve":
            if record.approver_id and record.approver_id != user_id:
                return False, "Only the assigned approver can approve"
            if record.status != RecordStatusEnum.UNDER_REVIEW:
                return False, f"Cannot approve from status: {record.status.value}"

        elif action == "revise":
            if record.doer_id and record.doer_id != user_id:
                return False, "Only the doer can revise"
            if record.status != RecordStatusEnum.REVISION_REQUIRED:
                return False, f"Cannot revise from status: {record.status.value}"

        return True, "Permission granted"
