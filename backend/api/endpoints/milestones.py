"""
Milestones and Deliverables API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.workflow import (
    Milestone,
    MilestoneStatusEnum,
    Deliverable
)
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

router = APIRouter()


# Pydantic schemas
class MilestoneCreate(BaseModel):
    project_id: int
    name: str
    description: Optional[str] = None
    due_date: date
    completion_criteria: Optional[str] = None
    owner_id: Optional[int] = None


class MilestoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[MilestoneStatusEnum] = None
    due_date: Optional[date] = None
    completed_date: Optional[date] = None
    completion_criteria: Optional[str] = None


class MilestoneResponse(BaseModel):
    id: int
    milestone_number: str
    project_id: int
    name: str
    status: str
    due_date: date
    completed_date: Optional[date]

    class Config:
        from_attributes = True


class DeliverableCreate(BaseModel):
    project_id: int
    milestone_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    due_date: Optional[date] = None
    owner_id: Optional[int] = None


class DeliverableResponse(BaseModel):
    id: int
    deliverable_number: str
    project_id: int
    name: str
    type: Optional[str]
    status: str
    due_date: Optional[date]

    class Config:
        from_attributes = True


# Milestone Endpoints

@router.post("/", response_model=MilestoneResponse)
async def create_milestone(
    milestone: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new milestone"""
    year = datetime.now().year
    count = db.query(Milestone).count() + 1
    milestone_number = f"MS-{year}-{count:04d}"

    new_milestone = Milestone(
        milestone_number=milestone_number,
        project_id=milestone.project_id,
        name=milestone.name,
        description=milestone.description,
        due_date=milestone.due_date,
        completion_criteria=milestone.completion_criteria,
        owner_id=milestone.owner_id or current_user.id,
        status=MilestoneStatusEnum.PENDING,
        created_by_id=current_user.id
    )

    db.add(new_milestone)
    db.commit()
    db.refresh(new_milestone)

    return new_milestone


@router.get("/", response_model=List[MilestoneResponse])
async def list_milestones(
    project_id: Optional[int] = None,
    status: Optional[MilestoneStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List milestones"""
    query = db.query(Milestone).filter(Milestone.is_deleted == False)

    if project_id:
        query = query.filter(Milestone.project_id == project_id)

    if status:
        query = query.filter(Milestone.status == status)

    milestones = query.offset(skip).limit(limit).all()
    return milestones


@router.get("/{milestone_id}", response_model=MilestoneResponse)
async def get_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get milestone details"""
    milestone = db.query(Milestone).filter(
        Milestone.id == milestone_id,
        Milestone.is_deleted == False
    ).first()

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

    return milestone


@router.put("/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: int,
    milestone_update: MilestoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update milestone"""
    milestone = db.query(Milestone).filter(
        Milestone.id == milestone_id,
        Milestone.is_deleted == False
    ).first()

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

    # Update fields
    if milestone_update.name:
        milestone.name = milestone_update.name
    if milestone_update.description is not None:
        milestone.description = milestone_update.description
    if milestone_update.status:
        milestone.status = milestone_update.status
        if milestone_update.status == MilestoneStatusEnum.COMPLETED:
            milestone.completed_date = datetime.now().date()
    if milestone_update.due_date:
        milestone.due_date = milestone_update.due_date
    if milestone_update.completed_date:
        milestone.completed_date = milestone_update.completed_date
    if milestone_update.completion_criteria is not None:
        milestone.completion_criteria = milestone_update.completion_criteria

    milestone.updated_by_id = current_user.id

    db.commit()
    db.refresh(milestone)

    return milestone


@router.delete("/{milestone_id}")
async def delete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete milestone"""
    milestone = db.query(Milestone).filter(
        Milestone.id == milestone_id,
        Milestone.is_deleted == False
    ).first()

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

    milestone.is_deleted = True
    milestone.updated_by_id = current_user.id

    db.commit()

    return {"message": "Milestone deleted successfully"}


# Deliverable Endpoints

@router.post("/deliverables", response_model=DeliverableResponse)
async def create_deliverable(
    deliverable: DeliverableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new deliverable"""
    year = datetime.now().year
    count = db.query(Deliverable).count() + 1
    deliverable_number = f"DEL-{year}-{count:04d}"

    new_deliverable = Deliverable(
        deliverable_number=deliverable_number,
        project_id=deliverable.project_id,
        milestone_id=deliverable.milestone_id,
        name=deliverable.name,
        description=deliverable.description,
        type=deliverable.type,
        due_date=deliverable.due_date,
        owner_id=deliverable.owner_id or current_user.id,
        status="pending",
        created_by_id=current_user.id
    )

    db.add(new_deliverable)
    db.commit()
    db.refresh(new_deliverable)

    return new_deliverable


@router.get("/deliverables", response_model=List[DeliverableResponse])
async def list_deliverables(
    project_id: Optional[int] = None,
    milestone_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List deliverables"""
    query = db.query(Deliverable).filter(Deliverable.is_deleted == False)

    if project_id:
        query = query.filter(Deliverable.project_id == project_id)

    if milestone_id:
        query = query.filter(Deliverable.milestone_id == milestone_id)

    if status:
        query = query.filter(Deliverable.status == status)

    deliverables = query.offset(skip).limit(limit).all()
    return deliverables


@router.put("/deliverables/{deliverable_id}/status")
async def update_deliverable_status(
    deliverable_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update deliverable status"""
    deliverable = db.query(Deliverable).filter(
        Deliverable.id == deliverable_id,
        Deliverable.is_deleted == False
    ).first()

    if not deliverable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deliverable not found"
        )

    deliverable.status = new_status

    if new_status == "completed":
        deliverable.submitted_date = datetime.now().date()
    elif new_status == "approved":
        deliverable.approved_date = datetime.now().date()

    deliverable.updated_by_id = current_user.id

    db.commit()

    return {"message": "Deliverable status updated successfully"}
