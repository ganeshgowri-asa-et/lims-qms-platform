"""
Time Tracking API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.workflow import TimeEntry, TaskComment
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

router = APIRouter()


class TimeEntryCreate(BaseModel):
    task_id: int
    entry_date: date
    hours: float
    description: Optional[str] = None
    billable: bool = True


class TimeEntryResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    entry_date: date
    hours: float
    description: Optional[str]
    billable: bool

    class Config:
        from_attributes = True


class TaskCommentCreate(BaseModel):
    task_id: int
    comment: str
    attachments: Optional[dict] = None


class TaskCommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    comment: str
    created_at: datetime

    class Config:
        from_attributes = True


# Time Entry Endpoints

@router.post("/", response_model=TimeEntryResponse)
async def create_time_entry(
    time_entry: TimeEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log time entry for a task"""
    new_entry = TimeEntry(
        task_id=time_entry.task_id,
        user_id=current_user.id,
        entry_date=time_entry.entry_date,
        hours=time_entry.hours,
        description=time_entry.description,
        billable=time_entry.billable,
        created_by_id=current_user.id
    )

    db.add(new_entry)

    # Update task actual hours
    from backend.models.workflow import Task

    task = db.query(Task).get(time_entry.task_id)
    if task:
        # Sum all time entries for this task
        total_hours = db.query(TimeEntry).filter(
            TimeEntry.task_id == time_entry.task_id
        ).with_entities(db.func.sum(TimeEntry.hours)).scalar() or 0

        task.actual_hours = float(total_hours) + time_entry.hours

    db.commit()
    db.refresh(new_entry)

    return new_entry


@router.get("/", response_model=List[TimeEntryResponse])
async def list_time_entries(
    task_id: Optional[int] = None,
    user_id: Optional[int] = None,
    entry_date_from: Optional[date] = None,
    entry_date_to: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List time entries"""
    query = db.query(TimeEntry).filter(TimeEntry.is_deleted == False)

    if task_id:
        query = query.filter(TimeEntry.task_id == task_id)

    if user_id:
        query = query.filter(TimeEntry.user_id == user_id)

    if entry_date_from:
        query = query.filter(TimeEntry.entry_date >= entry_date_from)

    if entry_date_to:
        query = query.filter(TimeEntry.entry_date <= entry_date_to)

    entries = query.offset(skip).limit(limit).all()
    return entries


@router.get("/summary")
async def get_time_tracking_summary(
    user_id: Optional[int] = None,
    task_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get time tracking summary"""
    query = db.query(TimeEntry).filter(TimeEntry.is_deleted == False)

    if user_id:
        query = query.filter(TimeEntry.user_id == user_id)

    if task_id:
        query = query.filter(TimeEntry.task_id == task_id)

    if date_from:
        query = query.filter(TimeEntry.entry_date >= date_from)

    if date_to:
        query = query.filter(TimeEntry.entry_date <= date_to)

    total_hours = query.with_entities(db.func.sum(TimeEntry.hours)).scalar() or 0
    billable_hours = query.filter(TimeEntry.billable == True).with_entities(
        db.func.sum(TimeEntry.hours)
    ).scalar() or 0
    non_billable_hours = query.filter(TimeEntry.billable == False).with_entities(
        db.func.sum(TimeEntry.hours)
    ).scalar() or 0

    return {
        "total_hours": float(total_hours),
        "billable_hours": float(billable_hours),
        "non_billable_hours": float(non_billable_hours),
        "entry_count": query.count()
    }


# Task Comment Endpoints

@router.post("/comments", response_model=TaskCommentResponse)
async def create_task_comment(
    comment: TaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add comment to a task"""
    new_comment = TaskComment(
        task_id=comment.task_id,
        user_id=current_user.id,
        comment=comment.comment,
        attachments=comment.attachments,
        created_by_id=current_user.id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


@router.get("/comments/{task_id}", response_model=List[TaskCommentResponse])
async def list_task_comments(
    task_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List comments for a task"""
    comments = db.query(TaskComment).filter(
        TaskComment.task_id == task_id,
        TaskComment.is_deleted == False
    ).order_by(TaskComment.created_at.desc()).offset(skip).limit(limit).all()

    return comments
