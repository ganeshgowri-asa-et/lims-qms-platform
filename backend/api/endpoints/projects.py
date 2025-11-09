"""
Project Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.workflow import Project, ProjectStatusEnum
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    customer_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[int] = None


class ProjectResponse(BaseModel):
    id: int
    project_number: str
    name: str
    status: str
    start_date: Optional[date]
    end_date: Optional[date]

    class Config:
        from_attributes = True


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new project"""
    year = datetime.now().year
    count = db.query(Project).count() + 1
    project_number = f"PRJ-{year}-{count:04d}"

    new_project = Project(
        project_number=project_number,
        name=project.name,
        description=project.description,
        customer_id=project.customer_id,
        project_manager_id=current_user.id,
        start_date=project.start_date,
        end_date=project.end_date,
        budget=project.budget,
        status=ProjectStatusEnum.PLANNING,
        created_by_id=current_user.id
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    status: Optional[ProjectStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all projects"""
    query = db.query(Project).filter(Project.is_deleted == False)

    if status:
        query = query.filter(Project.status == status)

    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project by ID"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.is_deleted == False
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project
