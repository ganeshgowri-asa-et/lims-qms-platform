"""
Workflow Engine - State machine implementation for custom workflows
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models.workflow import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowStepHistory,
    WorkflowStatusEnum,
    SLAViolation,
    RiskLevelEnum
)
from backend.models.user import User
import json


class WorkflowEngine:
    """
    Core workflow engine implementing state machine logic

    Features:
    - Define custom workflows with steps and transitions
    - Execute workflow instances
    - Handle conditional routing
    - Parallel and sequential step execution
    - SLA tracking and auto-escalation
    - Notifications at each step
    """

    def __init__(self, db: Session):
        self.db = db

    def create_workflow_definition(
        self,
        workflow_code: str,
        name: str,
        category: str,
        steps: List[Dict[str, Any]],
        initial_step: str,
        description: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        sla_config: Optional[Dict[str, Any]] = None,
        notification_config: Optional[Dict[str, Any]] = None,
        created_by_id: Optional[int] = None
    ) -> WorkflowDefinition:
        """
        Create a new workflow definition

        Steps format:
        [
            {
                "step_id": "step1",
                "name": "Initial Review",
                "type": "approval",  # approval, task, parallel, decision, automation
                "assignee_type": "role",  # role, user, dynamic
                "assignee_value": "manager",
                "next_steps": ["step2"],
                "conditions": {...},  # Optional routing conditions
                "config": {...}  # Step-specific configuration
            }
        ]
        """
        workflow = WorkflowDefinition(
            workflow_code=workflow_code,
            name=name,
            description=description,
            category=category,
            steps=steps,
            initial_step=initial_step,
            variables=variables,
            sla_config=sla_config,
            notification_config=notification_config,
            created_by_id=created_by_id
        )

        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)

        return workflow

    def start_workflow(
        self,
        workflow_definition_id: int,
        entity_type: str,
        entity_id: int,
        started_by_id: int,
        initial_variables: Optional[Dict[str, Any]] = None
    ) -> WorkflowInstance:
        """Start a new workflow instance"""
        definition = self.db.query(WorkflowDefinition).get(workflow_definition_id)

        if not definition:
            raise ValueError("Workflow definition not found")

        if not definition.is_active:
            raise ValueError("Workflow definition is not active")

        # Create instance
        instance_number = self._generate_instance_number()
        instance = WorkflowInstance(
            instance_number=instance_number,
            workflow_definition_id=workflow_definition_id,
            entity_type=entity_type,
            entity_id=entity_id,
            status=WorkflowStatusEnum.INITIATED,
            current_step=definition.initial_step,
            started_by_id=started_by_id,
            started_at=datetime.now(),
            variables=initial_variables or {},
            created_by_id=started_by_id
        )

        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)

        # Create first step history entry
        self._enter_step(instance, definition.initial_step)

        # Check SLA for first step
        self._check_sla(instance, definition.initial_step)

        # Send notifications
        self._send_step_notifications(instance, definition.initial_step, "entered")

        return instance

    def advance_workflow(
        self,
        instance_id: int,
        action: str,
        user_id: int,
        data: Optional[Dict[str, Any]] = None,
        comments: Optional[str] = None
    ) -> WorkflowInstance:
        """
        Advance workflow to next step based on action taken

        Actions: approve, reject, complete, skip, etc.
        """
        instance = self.db.query(WorkflowInstance).get(instance_id)

        if not instance:
            raise ValueError("Workflow instance not found")

        if instance.status not in [WorkflowStatusEnum.INITIATED, WorkflowStatusEnum.IN_PROGRESS]:
            raise ValueError(f"Cannot advance workflow in status: {instance.status}")

        definition = instance.definition
        current_step_id = instance.current_step

        # Complete current step
        self._complete_step(instance, current_step_id, user_id, action, data, comments)

        # Determine next step(s)
        current_step_config = self._get_step_config(definition, current_step_id)
        next_steps = self._evaluate_next_steps(
            current_step_config,
            action,
            instance.variables,
            data
        )

        if not next_steps:
            # Workflow completed
            instance.status = WorkflowStatusEnum.COMPLETED
            instance.completed_at = datetime.now()
            instance.current_step = None
        elif len(next_steps) == 1:
            # Single next step
            instance.current_step = next_steps[0]
            instance.status = WorkflowStatusEnum.IN_PROGRESS
            self._enter_step(instance, next_steps[0])
            self._check_sla(instance, next_steps[0])
            self._send_step_notifications(instance, next_steps[0], "entered")
        else:
            # Parallel steps - create sub-instances or handle differently
            # For simplicity, we'll take the first step
            instance.current_step = next_steps[0]
            instance.status = WorkflowStatusEnum.IN_PROGRESS
            self._enter_step(instance, next_steps[0])
            self._check_sla(instance, next_steps[0])
            self._send_step_notifications(instance, next_steps[0], "entered")

        self.db.commit()
        self.db.refresh(instance)

        return instance

    def cancel_workflow(
        self,
        instance_id: int,
        user_id: int,
        reason: Optional[str] = None
    ) -> WorkflowInstance:
        """Cancel a workflow instance"""
        instance = self.db.query(WorkflowInstance).get(instance_id)

        if not instance:
            raise ValueError("Workflow instance not found")

        instance.status = WorkflowStatusEnum.CANCELLED
        instance.completed_at = datetime.now()

        # Log cancellation
        if instance.current_step:
            self._complete_step(
                instance,
                instance.current_step,
                user_id,
                "cancelled",
                {},
                reason
            )

        self.db.commit()
        self.db.refresh(instance)

        return instance

    def pause_workflow(self, instance_id: int) -> WorkflowInstance:
        """Pause a workflow instance"""
        instance = self.db.query(WorkflowInstance).get(instance_id)

        if not instance:
            raise ValueError("Workflow instance not found")

        instance.status = WorkflowStatusEnum.PAUSED
        self.db.commit()
        self.db.refresh(instance)

        return instance

    def resume_workflow(self, instance_id: int) -> WorkflowInstance:
        """Resume a paused workflow instance"""
        instance = self.db.query(WorkflowInstance).get(instance_id)

        if not instance:
            raise ValueError("Workflow instance not found")

        if instance.status != WorkflowStatusEnum.PAUSED:
            raise ValueError("Workflow is not paused")

        instance.status = WorkflowStatusEnum.IN_PROGRESS
        self.db.commit()
        self.db.refresh(instance)

        return instance

    def get_workflow_status(self, instance_id: int) -> Dict[str, Any]:
        """Get current status of workflow instance"""
        instance = self.db.query(WorkflowInstance).get(instance_id)

        if not instance:
            raise ValueError("Workflow instance not found")

        history = self.db.query(WorkflowStepHistory).filter(
            WorkflowStepHistory.instance_id == instance_id
        ).order_by(WorkflowStepHistory.entered_at).all()

        return {
            "instance_number": instance.instance_number,
            "status": instance.status.value,
            "current_step": instance.current_step,
            "started_at": instance.started_at.isoformat() if instance.started_at else None,
            "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
            "variables": instance.variables,
            "history": [
                {
                    "step_id": h.step_id,
                    "step_name": h.step_name,
                    "status": h.status,
                    "entered_at": h.entered_at.isoformat() if h.entered_at else None,
                    "completed_at": h.completed_at.isoformat() if h.completed_at else None,
                    "action_taken": h.action_taken,
                    "comments": h.comments
                }
                for h in history
            ]
        }

    def check_sla_violations(self) -> List[SLAViolation]:
        """Check for SLA violations across all active workflows"""
        violations = []

        active_instances = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.status.in_([
                WorkflowStatusEnum.INITIATED,
                WorkflowStatusEnum.IN_PROGRESS
            ])
        ).all()

        for instance in active_instances:
            definition = instance.definition
            current_step = instance.current_step

            if not definition.sla_config or current_step not in definition.sla_config:
                continue

            sla = definition.sla_config[current_step]
            duration_hours = sla.get("duration_hours", 24)

            # Get when step was entered
            step_history = self.db.query(WorkflowStepHistory).filter(
                WorkflowStepHistory.instance_id == instance.id,
                WorkflowStepHistory.step_id == current_step,
                WorkflowStepHistory.status == "entered"
            ).order_by(WorkflowStepHistory.entered_at.desc()).first()

            if step_history and step_history.entered_at:
                expected_completion = step_history.entered_at + timedelta(hours=duration_hours)

                if datetime.now() > expected_completion:
                    # SLA violated
                    violation_hours = (datetime.now() - expected_completion).total_seconds() / 3600

                    # Check if already logged
                    existing = self.db.query(SLAViolation).filter(
                        SLAViolation.workflow_instance_id == instance.id,
                        SLAViolation.entity_type == "workflow_step",
                        SLAViolation.entity_id == step_history.id
                    ).first()

                    if not existing:
                        severity = self._calculate_violation_severity(violation_hours)

                        violation = SLAViolation(
                            workflow_instance_id=instance.id,
                            entity_type="workflow_step",
                            entity_id=step_history.id,
                            sla_type="step_completion",
                            expected_completion=expected_completion,
                            violation_duration_hours=violation_hours,
                            severity=severity,
                            created_by_id=instance.started_by_id
                        )

                        self.db.add(violation)
                        violations.append(violation)

                        # Handle escalation
                        self._handle_escalation(instance, violation, sla)

        if violations:
            self.db.commit()

        return violations

    # Private helper methods

    def _generate_instance_number(self) -> str:
        """Generate unique instance number"""
        from datetime import datetime
        year = datetime.now().year
        count = self.db.query(WorkflowInstance).count() + 1
        return f"WF-{year}-{count:06d}"

    def _get_step_config(self, definition: WorkflowDefinition, step_id: str) -> Dict[str, Any]:
        """Get step configuration from definition"""
        for step in definition.steps:
            if step["step_id"] == step_id:
                return step
        raise ValueError(f"Step {step_id} not found in workflow definition")

    def _enter_step(self, instance: WorkflowInstance, step_id: str):
        """Create history entry for entering a step"""
        definition = instance.definition
        step_config = self._get_step_config(definition, step_id)

        # Determine assignee
        assigned_to_id = self._resolve_assignee(
            instance,
            step_config.get("assignee_type"),
            step_config.get("assignee_value")
        )

        history = WorkflowStepHistory(
            instance_id=instance.id,
            step_id=step_id,
            step_name=step_config["name"],
            status="entered",
            entered_at=datetime.now(),
            assigned_to_id=assigned_to_id,
            created_by_id=instance.started_by_id
        )

        self.db.add(history)

    def _complete_step(
        self,
        instance: WorkflowInstance,
        step_id: str,
        user_id: int,
        action: str,
        data: Optional[Dict[str, Any]],
        comments: Optional[str]
    ):
        """Mark step as completed"""
        # Find the entered history record
        history = self.db.query(WorkflowStepHistory).filter(
            WorkflowStepHistory.instance_id == instance.id,
            WorkflowStepHistory.step_id == step_id,
            WorkflowStepHistory.status == "entered"
        ).order_by(WorkflowStepHistory.entered_at.desc()).first()

        if history:
            history.status = "completed"
            history.completed_at = datetime.now()
            history.action_taken = action
            history.comments = comments
            history.data = data
            history.updated_by_id = user_id

    def _evaluate_next_steps(
        self,
        current_step: Dict[str, Any],
        action: str,
        variables: Dict[str, Any],
        action_data: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Evaluate next steps based on conditions"""
        next_steps = current_step.get("next_steps", [])
        conditions = current_step.get("conditions", {})

        if not conditions:
            return next_steps

        # Simple condition evaluation
        # In production, this would be more sophisticated
        if action in conditions:
            return conditions[action]

        return next_steps

    def _resolve_assignee(
        self,
        instance: WorkflowInstance,
        assignee_type: Optional[str],
        assignee_value: Optional[str]
    ) -> Optional[int]:
        """Resolve assignee based on type and value"""
        if not assignee_type:
            return None

        if assignee_type == "user":
            return int(assignee_value) if assignee_value else None

        if assignee_type == "role":
            # Find first user with this role
            # This would integrate with your role system
            return None

        if assignee_type == "dynamic":
            # Resolve from instance variables
            return instance.variables.get(assignee_value)

        return None

    def _check_sla(self, instance: WorkflowInstance, step_id: str):
        """Check and set up SLA tracking for a step"""
        definition = instance.definition

        if not definition.sla_config or step_id not in definition.sla_config:
            return

        # SLA tracking happens in check_sla_violations()

    def _send_step_notifications(
        self,
        instance: WorkflowInstance,
        step_id: str,
        event: str
    ):
        """Send notifications for step events"""
        definition = instance.definition

        if not definition.notification_config or step_id not in definition.notification_config:
            return

        # Notification sending would be implemented here
        # This would integrate with the notification system

    def _calculate_violation_severity(self, violation_hours: float) -> RiskLevelEnum:
        """Calculate severity of SLA violation"""
        if violation_hours > 48:
            return RiskLevelEnum.CRITICAL
        elif violation_hours > 24:
            return RiskLevelEnum.HIGH
        elif violation_hours > 8:
            return RiskLevelEnum.MEDIUM
        else:
            return RiskLevelEnum.LOW

    def _handle_escalation(
        self,
        instance: WorkflowInstance,
        violation: SLAViolation,
        sla_config: Dict[str, Any]
    ):
        """Handle escalation for SLA violation"""
        escalation_rules = sla_config.get("escalation_rules", {})

        if not escalation_rules:
            return

        # Simple escalation: notify manager
        escalate_to_id = escalation_rules.get("escalate_to_user_id")

        if escalate_to_id:
            violation.escalated = True
            violation.escalated_to_id = escalate_to_id
            # Send escalation notification
