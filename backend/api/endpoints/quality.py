"""
Quality Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.quality import NonConformance, CAPA, Audit, NCStatusEnum, CAPAStatusEnum
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

router = APIRouter()


class NCCreate(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    severity: str
    detected_date: date


class CAPACreate(BaseModel):
    title: str
    capa_type: str
    description: str
    proposed_action: str
    target_completion_date: Optional[date] = None


@router.post("/nc", response_model=dict)
async def create_nc(
    nc: NCCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create Non-Conformance"""
    year = datetime.now().year
    count = db.query(NonConformance).count() + 1
    nc_number = f"NC-{year}-{count:04d}"

    new_nc = NonConformance(
        nc_number=nc_number,
        title=nc.title,
        description=nc.description,
        category=nc.category,
        severity=nc.severity,
        detected_date=nc.detected_date,
        detected_by_id=current_user.id,
        status=NCStatusEnum.OPEN,
        created_by_id=current_user.id
    )

    db.add(new_nc)
    db.commit()

    return {
        "message": "Non-Conformance created successfully",
        "nc_number": nc_number
    }


@router.get("/nc", response_model=List[dict])
async def list_ncs(
    status: Optional[NCStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List Non-Conformances"""
    query = db.query(NonConformance).filter(NonConformance.is_deleted == False)

    if status:
        query = query.filter(NonConformance.status == status)

    ncs = query.offset(skip).limit(limit).all()

    return [
        {
            "id": nc.id,
            "nc_number": nc.nc_number,
            "title": nc.title,
            "severity": nc.severity.value,
            "status": nc.status.value
        }
        for nc in ncs
    ]


@router.post("/capa", response_model=dict)
async def create_capa(
    capa: CAPACreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create CAPA"""
    year = datetime.now().year
    count = db.query(CAPA).count() + 1
    capa_number = f"CAPA-{year}-{count:04d}"

    new_capa = CAPA(
        capa_number=capa_number,
        title=capa.title,
        capa_type=capa.capa_type,
        description=capa.description,
        proposed_action=capa.proposed_action,
        target_completion_date=capa.target_completion_date,
        responsible_person_id=current_user.id,
        status=CAPAStatusEnum.OPEN,
        created_by_id=current_user.id
    )

    db.add(new_capa)
    db.commit()

    return {
        "message": "CAPA created successfully",
        "capa_number": capa_number
    }


@router.get("/capa", response_model=List[dict])
async def list_capas(
    status: Optional[CAPAStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List CAPAs"""
    query = db.query(CAPA).filter(CAPA.is_deleted == False)

    if status:
        query = query.filter(CAPA.status == status)

    capas = query.offset(skip).limit(limit).all()

    return [
        {
            "id": c.id,
            "capa_number": c.capa_number,
            "title": c.title,
            "capa_type": c.capa_type,
            "status": c.status.value
        }
        for c in capas
    ]
