"""
Workflow service for Doer-Checker-Approver pattern
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional

from app.models.base import WorkflowRecord, WorkflowStatus, User
from app.core.security import get_password_hash
import hashlib


class WorkflowService:
    """Service for managing workflow operations"""

    @staticmethod
    async def create_workflow(
        db: AsyncSession, table_name: str, record_id: int, doer_id: int
    ) -> WorkflowRecord:
        """Create new workflow record for Doer-Checker-Approver"""
        workflow = WorkflowRecord(
            table_name=table_name,
            record_id=record_id,
            status=WorkflowStatus.DRAFT,
            doer_id=doer_id,
            doer_timestamp=datetime.now(),
        )

        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)

        return workflow

    @staticmethod
    async def get_workflow(
        db: AsyncSession, table_name: str, record_id: int
    ) -> Optional[WorkflowRecord]:
        """Get workflow record for a specific table and record"""
        result = await db.execute(
            select(WorkflowRecord).where(
                WorkflowRecord.table_name == table_name,
                WorkflowRecord.record_id == record_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def submit_for_checking(
        db: AsyncSession,
        workflow_id: int,
        doer_id: int,
        comments: Optional[str] = None,
        signature_data: Optional[str] = None,
    ) -> WorkflowRecord:
        """Doer submits record for checking"""
        result = await db.execute(
            select(WorkflowRecord).where(WorkflowRecord.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise ValueError("Workflow not found")

        if workflow.doer_id != doer_id:
            raise ValueError("Only the doer can submit this record")

        if workflow.status not in [WorkflowStatus.DRAFT, WorkflowStatus.REVISION_REQUIRED]:
            raise ValueError(f"Cannot submit record in status: {workflow.status}")

        workflow.status = WorkflowStatus.SUBMITTED
        workflow.doer_timestamp = datetime.now()
        workflow.doer_comments = comments

        if signature_data:
            # Create signature hash
            signature_hash = hashlib.sha256(
                f"{doer_id}{datetime.now().isoformat()}{signature_data}".encode()
            ).hexdigest()
            workflow.doer_signature = signature_hash

        await db.commit()
        await db.refresh(workflow)

        return workflow

    @staticmethod
    async def check_record(
        db: AsyncSession,
        workflow_id: int,
        checker_id: int,
        approved: bool,
        comments: Optional[str] = None,
        signature_data: Optional[str] = None,
    ) -> WorkflowRecord:
        """Checker reviews the record"""
        result = await db.execute(
            select(WorkflowRecord).where(WorkflowRecord.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise ValueError("Workflow not found")

        if workflow.status != WorkflowStatus.SUBMITTED:
            raise ValueError(f"Cannot check record in status: {workflow.status}")

        workflow.checker_id = checker_id
        workflow.checker_timestamp = datetime.now()
        workflow.checker_comments = comments

        if signature_data:
            signature_hash = hashlib.sha256(
                f"{checker_id}{datetime.now().isoformat()}{signature_data}".encode()
            ).hexdigest()
            workflow.checker_signature = signature_hash

        if approved:
            workflow.status = WorkflowStatus.CHECKED
        else:
            workflow.status = WorkflowStatus.REVISION_REQUIRED

        await db.commit()
        await db.refresh(workflow)

        return workflow

    @staticmethod
    async def approve_record(
        db: AsyncSession,
        workflow_id: int,
        approver_id: int,
        approved: bool,
        comments: Optional[str] = None,
        signature_data: Optional[str] = None,
    ) -> WorkflowRecord:
        """Approver gives final approval"""
        result = await db.execute(
            select(WorkflowRecord).where(WorkflowRecord.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise ValueError("Workflow not found")

        if workflow.status != WorkflowStatus.CHECKED:
            raise ValueError(f"Cannot approve record in status: {workflow.status}")

        workflow.approver_id = approver_id
        workflow.approver_timestamp = datetime.now()
        workflow.approver_comments = comments

        if signature_data:
            signature_hash = hashlib.sha256(
                f"{approver_id}{datetime.now().isoformat()}{signature_data}".encode()
            ).hexdigest()
            workflow.approver_signature = signature_hash

        if approved:
            workflow.status = WorkflowStatus.APPROVED
        else:
            workflow.status = WorkflowStatus.REJECTED
            workflow.rejected_by_id = approver_id
            workflow.rejection_timestamp = datetime.now()

        await db.commit()
        await db.refresh(workflow)

        return workflow

    @staticmethod
    async def reject_record(
        db: AsyncSession,
        workflow_id: int,
        rejector_id: int,
        reason: str,
        comments: Optional[str] = None,
    ) -> WorkflowRecord:
        """Reject record at any stage"""
        result = await db.execute(
            select(WorkflowRecord).where(WorkflowRecord.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise ValueError("Workflow not found")

        if workflow.status in [WorkflowStatus.APPROVED, WorkflowStatus.REJECTED]:
            raise ValueError(f"Cannot reject record in status: {workflow.status}")

        workflow.status = WorkflowStatus.REJECTED
        workflow.rejected_by_id = rejector_id
        workflow.rejection_timestamp = datetime.now()
        workflow.rejection_reason = reason

        if comments:
            # Append to appropriate comments field based on rejector role
            if workflow.checker_id == rejector_id:
                workflow.checker_comments = comments
            elif workflow.approver_id == rejector_id:
                workflow.approver_comments = comments

        await db.commit()
        await db.refresh(workflow)

        return workflow

    @staticmethod
    async def get_pending_checks(
        db: AsyncSession, limit: int = 100
    ) -> list[WorkflowRecord]:
        """Get all records pending checker review"""
        result = await db.execute(
            select(WorkflowRecord)
            .where(WorkflowRecord.status == WorkflowStatus.SUBMITTED)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_pending_approvals(
        db: AsyncSession, limit: int = 100
    ) -> list[WorkflowRecord]:
        """Get all records pending final approval"""
        result = await db.execute(
            select(WorkflowRecord)
            .where(WorkflowRecord.status == WorkflowStatus.CHECKED)
            .limit(limit)
        )
        return result.scalars().all()
