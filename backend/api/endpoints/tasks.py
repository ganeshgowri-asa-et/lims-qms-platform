"""
Task Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.workflow import Task, TaskStatusEnum, TaskPriorityEnum
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

router = APIRouter()


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM
    due_date: Optional[date] = None


class TaskResponse(BaseModel):
    id: int
    task_number: str
    title: str
    status: str
    priority: str
    due_date: Optional[date]

    class Config:
        from_attributes = True


@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task"""
    year = datetime.now().year
    count = db.query(Task).count() + 1
    task_number = f"TASK-{year}-{count:04d}"

    new_task = Task(
        task_number=task_number,
        title=task.title,
        description=task.description,
        project_id=task.project_id,
        assigned_to_id=task.assigned_to_id or current_user.id,
        priority=task.priority,
        status=TaskStatusEnum.TODO,
        due_date=task.due_date,
        created_by_id=current_user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    project_id: Optional[int] = None,
    status: Optional[TaskStatusEnum] = None,
    assigned_to_me: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List tasks with filters"""
    query = db.query(Task).filter(Task.is_deleted == False)

    if project_id:
        query = query.filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == status)
    if assigned_to_me:
        query = query.filter(Task.assigned_to_id == current_user.id)

    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.put("/{task_id}/status")
async def update_task_status(
    task_id: int,
    new_status: TaskStatusEnum,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update task status"""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task.status = new_status
    if new_status == TaskStatusEnum.COMPLETED:
        task.progress = 100

    db.commit()

    return {"message": "Task status updated successfully"}
