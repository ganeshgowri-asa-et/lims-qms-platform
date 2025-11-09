"""
Workflow Engine API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.workflow import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowStepHistory,
    WorkflowStatusEnum
)
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from backend.services.workflow_engine import WorkflowEngine
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter()


# Pydantic schemas
class WorkflowDefinitionCreate(BaseModel):
    workflow_code: str
    name: str
    category: str
    description: Optional[str] = None
    steps: List[Dict[str, Any]]
    initial_step: str
    variables: Optional[Dict[str, Any]] = None
    sla_config: Optional[Dict[str, Any]] = None
    notification_config: Optional[Dict[str, Any]] = None


class WorkflowDefinitionResponse(BaseModel):
    id: int
    workflow_code: str
    name: str
    category: str
    is_active: bool

    class Config:
        from_attributes = True


class WorkflowInstanceCreate(BaseModel):
    workflow_definition_id: int
    entity_type: str
    entity_id: int
    initial_variables: Optional[Dict[str, Any]] = None


class WorkflowInstanceResponse(BaseModel):
    id: int
    instance_number: str
    status: str
    current_step: Optional[str]
    started_at: Optional[datetime]

    class Config:
        from_attributes = True


class WorkflowActionRequest(BaseModel):
    action: str
    data: Optional[Dict[str, Any]] = None
    comments: Optional[str] = None


# Workflow Definition Endpoints

@router.post("/definitions", response_model=WorkflowDefinitionResponse)
async def create_workflow_definition(
    workflow_def: WorkflowDefinitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new workflow definition"""
    engine = WorkflowEngine(db)

    try:
        definition = engine.create_workflow_definition(
            workflow_code=workflow_def.workflow_code,
            name=workflow_def.name,
            category=workflow_def.category,
            description=workflow_def.description,
            steps=workflow_def.steps,
            initial_step=workflow_def.initial_step,
            variables=workflow_def.variables,
            sla_config=workflow_def.sla_config,
            notification_config=workflow_def.notification_config,
            created_by_id=current_user.id
        )

        return definition

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/definitions", response_model=List[WorkflowDefinitionResponse])
async def list_workflow_definitions(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workflow definitions"""
    query = db.query(WorkflowDefinition).filter(WorkflowDefinition.is_deleted == False)

    if category:
        query = query.filter(WorkflowDefinition.category == category)

    if is_active is not None:
        query = query.filter(WorkflowDefinition.is_active == is_active)

    definitions = query.offset(skip).limit(limit).all()
    return definitions


@router.get("/definitions/{definition_id}")
async def get_workflow_definition(
    definition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workflow definition details"""
    definition = db.query(WorkflowDefinition).filter(
        WorkflowDefinition.id == definition_id,
        WorkflowDefinition.is_deleted == False
    ).first()

    if not definition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow definition not found"
        )

    return {
        "id": definition.id,
        "workflow_code": definition.workflow_code,
        "name": definition.name,
        "description": definition.description,
        "category": definition.category,
        "version": definition.version,
        "steps": definition.steps,
        "initial_step": definition.initial_step,
        "variables": definition.variables,
        "sla_config": definition.sla_config,
        "notification_config": definition.notification_config,
        "is_active": definition.is_active
    }


# Workflow Instance Endpoints

@router.post("/instances", response_model=WorkflowInstanceResponse)
async def start_workflow_instance(
    instance_data: WorkflowInstanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new workflow instance"""
    engine = WorkflowEngine(db)

    try:
        instance = engine.start_workflow(
            workflow_definition_id=instance_data.workflow_definition_id,
            entity_type=instance_data.entity_type,
            entity_id=instance_data.entity_id,
            started_by_id=current_user.id,
            initial_variables=instance_data.initial_variables
        )

        return instance

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/instances", response_model=List[WorkflowInstanceResponse])
async def list_workflow_instances(
    workflow_definition_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    status: Optional[WorkflowStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workflow instances"""
    query = db.query(WorkflowInstance).filter(WorkflowInstance.is_deleted == False)

    if workflow_definition_id:
        query = query.filter(WorkflowInstance.workflow_definition_id == workflow_definition_id)

    if entity_type:
        query = query.filter(WorkflowInstance.entity_type == entity_type)

    if entity_id:
        query = query.filter(WorkflowInstance.entity_id == entity_id)

    if status:
        query = query.filter(WorkflowInstance.status == status)

    instances = query.offset(skip).limit(limit).all()
    return instances


@router.get("/instances/{instance_id}/status")
async def get_workflow_instance_status(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workflow instance status and history"""
    engine = WorkflowEngine(db)

    try:
        status_data = engine.get_workflow_status(instance_id)
        return status_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/instances/{instance_id}/advance")
async def advance_workflow_instance(
    instance_id: int,
    action_request: WorkflowActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Advance workflow to next step"""
    engine = WorkflowEngine(db)

    try:
        instance = engine.advance_workflow(
            instance_id=instance_id,
            action=action_request.action,
            user_id=current_user.id,
            data=action_request.data,
            comments=action_request.comments
        )

        return {
            "id": instance.id,
            "instance_number": instance.instance_number,
            "status": instance.status.value,
            "current_step": instance.current_step,
            "message": "Workflow advanced successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/instances/{instance_id}/cancel")
async def cancel_workflow_instance(
    instance_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a workflow instance"""
    engine = WorkflowEngine(db)

    try:
        instance = engine.cancel_workflow(
            instance_id=instance_id,
            user_id=current_user.id,
            reason=reason
        )

        return {
            "id": instance.id,
            "status": instance.status.value,
            "message": "Workflow cancelled successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/instances/{instance_id}/pause")
async def pause_workflow_instance(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pause a workflow instance"""
    engine = WorkflowEngine(db)

    try:
        instance = engine.pause_workflow(instance_id)

        return {
            "id": instance.id,
            "status": instance.status.value,
            "message": "Workflow paused successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/instances/{instance_id}/resume")
async def resume_workflow_instance(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resume a paused workflow instance"""
    engine = WorkflowEngine(db)

    try:
        instance = engine.resume_workflow(instance_id)

        return {
            "id": instance.id,
            "status": instance.status.value,
            "message": "Workflow resumed successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/sla-violations")
async def check_sla_violations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check for SLA violations"""
    engine = WorkflowEngine(db)
    violations = engine.check_sla_violations()

    return {
        "violations_found": len(violations),
        "violations": [
            {
                "id": v.id,
                "workflow_instance_id": v.workflow_instance_id,
                "task_id": v.task_id,
                "entity_type": v.entity_type,
                "entity_id": v.entity_id,
                "sla_type": v.sla_type,
                "expected_completion": v.expected_completion.isoformat() if v.expected_completion else None,
                "violation_duration_hours": v.violation_duration_hours,
                "severity": v.severity.value,
                "escalated": v.escalated
            }
            for v in violations
        ]
    }
