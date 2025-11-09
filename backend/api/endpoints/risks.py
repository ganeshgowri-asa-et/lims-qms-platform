"""
Risk Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.workflow import Risk, RiskLevelEnum
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

router = APIRouter()


class RiskCreate(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    probability: RiskLevelEnum
    impact: RiskLevelEnum
    mitigation_plan: Optional[str] = None
    contingency_plan: Optional[str] = None
    owner_id: Optional[int] = None


class RiskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    probability: Optional[RiskLevelEnum] = None
    impact: Optional[RiskLevelEnum] = None
    status: Optional[str] = None
    mitigation_plan: Optional[str] = None
    contingency_plan: Optional[str] = None


class RiskResponse(BaseModel):
    id: int
    risk_number: str
    project_id: int
    title: str
    category: Optional[str]
    probability: str
    impact: str
    overall_risk_level: Optional[str]
    status: str

    class Config:
        from_attributes = True


@router.post("/", response_model=RiskResponse)
async def create_risk(
    risk: RiskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new risk"""
    year = datetime.now().year
    count = db.query(Risk).count() + 1
    risk_number = f"RISK-{year}-{count:04d}"

    # Calculate overall risk level
    risk_matrix = {
        ("Low", "Low"): "Low",
        ("Low", "Medium"): "Low",
        ("Low", "High"): "Medium",
        ("Low", "Critical"): "Medium",
        ("Medium", "Low"): "Low",
        ("Medium", "Medium"): "Medium",
        ("Medium", "High"): "High",
        ("Medium", "Critical"): "High",
        ("High", "Low"): "Medium",
        ("High", "Medium"): "High",
        ("High", "High"): "High",
        ("High", "Critical"): "Critical",
        ("Critical", "Low"): "Medium",
        ("Critical", "Medium"): "High",
        ("Critical", "High"): "Critical",
        ("Critical", "Critical"): "Critical",
    }

    overall_risk_level = risk_matrix.get(
        (risk.probability.value, risk.impact.value),
        "Medium"
    )

    new_risk = Risk(
        risk_number=risk_number,
        project_id=risk.project_id,
        title=risk.title,
        description=risk.description,
        category=risk.category,
        probability=risk.probability,
        impact=risk.impact,
        overall_risk_level=overall_risk_level,
        mitigation_plan=risk.mitigation_plan,
        contingency_plan=risk.contingency_plan,
        owner_id=risk.owner_id or current_user.id,
        identified_date=datetime.now().date(),
        status="identified",
        created_by_id=current_user.id
    )

    db.add(new_risk)
    db.commit()
    db.refresh(new_risk)

    return new_risk


@router.get("/", response_model=List[RiskResponse])
async def list_risks(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    overall_risk_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List risks"""
    query = db.query(Risk).filter(Risk.is_deleted == False)

    if project_id:
        query = query.filter(Risk.project_id == project_id)

    if status:
        query = query.filter(Risk.status == status)

    if category:
        query = query.filter(Risk.category == category)

    if overall_risk_level:
        query = query.filter(Risk.overall_risk_level == overall_risk_level)

    risks = query.offset(skip).limit(limit).all()
    return risks


@router.put("/{risk_id}", response_model=RiskResponse)
async def update_risk(
    risk_id: int,
    risk_update: RiskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update risk"""
    risk = db.query(Risk).filter(
        Risk.id == risk_id,
        Risk.is_deleted == False
    ).first()

    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found"
        )

    # Update fields
    update_data = risk_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(risk, field, value)

    # Recalculate overall risk level if probability or impact changed
    if risk_update.probability or risk_update.impact:
        risk_matrix = {
            ("Low", "Low"): "Low",
            ("Low", "Medium"): "Low",
            ("Low", "High"): "Medium",
            ("Low", "Critical"): "Medium",
            ("Medium", "Low"): "Low",
            ("Medium", "Medium"): "Medium",
            ("Medium", "High"): "High",
            ("Medium", "Critical"): "High",
            ("High", "Low"): "Medium",
            ("High", "Medium"): "High",
            ("High", "High"): "High",
            ("High", "Critical"): "Critical",
            ("Critical", "Low"): "Medium",
            ("Critical", "Medium"): "High",
            ("Critical", "High"): "Critical",
            ("Critical", "Critical"): "Critical",
        }

        risk.overall_risk_level = risk_matrix.get(
            (risk.probability.value, risk.impact.value),
            "Medium"
        )

    if risk_update.status == "closed":
        risk.closed_date = datetime.now().date()

    risk.updated_by_id = current_user.id

    db.commit()
    db.refresh(risk)

    return risk
