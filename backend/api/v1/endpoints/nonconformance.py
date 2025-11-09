"""
Non-Conformance & CAPA API (Session 7)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.nonconformance import NonConformance, RootCauseAnalysis, CAPAAction
from backend.models.common import AuditLog


router = APIRouter()


class NCCreate(BaseModel):
    nc_category: str
    detected_date: date
    detected_by_id: int
    description: str
    immediate_action: str = None
    severity: str


class NCResponse(BaseModel):
    id: int
    nc_number: str
    nc_category: str
    status: str
    severity: str

    class Config:
        from_attributes = True


class RCACreate(BaseModel):
    nc_id: int
    analysis_method: str
    why_1: str = None
    why_2: str = None
    why_3: str = None
    why_4: str = None
    why_5: str = None
    root_cause: str
    analyzed_by_id: int


class CAPACreate(BaseModel):
    nc_id: int
    action_type: str
    action_description: str
    responsible_person_id: int
    target_date: date


@router.post("/", response_model=NCResponse)
def create_nonconformance(nc: NCCreate, db: Session = Depends(get_db)):
    """Create non-conformance with auto-generated NC number"""

    # Generate NC number: NC-YYYY-XXX
    year = datetime.now().year
    last_nc = db.query(NonConformance).filter(
        NonConformance.nc_number.like(f"NC-{year}-%")
    ).order_by(NonConformance.id.desc()).first()

    if last_nc:
        last_num = int(last_nc.nc_number.split("-")[-1])
        nc_number = f"NC-{year}-{last_num + 1:03d}"
    else:
        nc_number = f"NC-{year}-001"

    db_nc = NonConformance(
        nc_number=nc_number,
        nc_category=nc.nc_category,
        detected_date=nc.detected_date,
        detected_by_id=nc.detected_by_id,
        description=nc.description,
        immediate_action=nc.immediate_action,
        severity=nc.severity
    )

    db.add(db_nc)
    db.commit()
    db.refresh(db_nc)

    # TODO: Generate AI suggested root cause
    # ai_suggestion = ai_suggest_root_cause(nc.description, nc.nc_category)
    # db_nc.ai_suggested_root_cause = ai_suggestion
    # db.commit()

    # Audit log
    audit_log = AuditLog(
        user_id=nc.detected_by_id,
        module="nonconformance",
        action="create",
        entity_type="nonconformances",
        entity_id=db_nc.id,
        description=f"Created NC {nc_number}"
    )
    db.add(audit_log)
    db.commit()

    return db_nc


@router.get("/", response_model=List[NCResponse])
def list_nonconformances(
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List non-conformances with filters"""
    query = db.query(NonConformance)

    if status:
        query = query.filter(NonConformance.status == status)

    ncs = query.offset(skip).limit(limit).all()
    return ncs


@router.post("/root-cause-analysis")
def create_rca(rca: RCACreate, db: Session = Depends(get_db)):
    """Create root cause analysis (5-Why/Fishbone)"""

    db_rca = RootCauseAnalysis(
        **rca.dict(),
        analysis_date=date.today()
    )

    db.add(db_rca)

    # Update NC status
    nc = db.query(NonConformance).filter(NonConformance.id == rca.nc_id).first()
    if nc:
        nc.status = "under_investigation"

    db.commit()

    return {"message": "Root cause analysis created"}


@router.post("/capa")
def create_capa(capa: CAPACreate, db: Session = Depends(get_db)):
    """Create CAPA action"""

    # Generate CAPA number
    year = datetime.now().year
    last_capa = db.query(CAPAAction).filter(
        CAPAAction.capa_number.like(f"CAPA-{year}-%")
    ).order_by(CAPAAction.id.desc()).first()

    if last_capa:
        last_num = int(last_capa.capa_number.split("-")[-1])
        capa_number = f"CAPA-{year}-{last_num + 1:03d}"
    else:
        capa_number = f"CAPA-{year}-001"

    db_capa = CAPAAction(
        capa_number=capa_number,
        **capa.dict(),
        status="planned"
    )

    db.add(db_capa)

    # Update NC status
    nc = db.query(NonConformance).filter(NonConformance.id == capa.nc_id).first()
    if nc:
        nc.status = "capa_in_progress"

    db.commit()

    return {"message": "CAPA action created", "capa_number": capa_number}


@router.put("/capa/{capa_id}/complete")
def complete_capa(capa_id: int, db: Session = Depends(get_db)):
    """Mark CAPA as completed"""

    capa = db.query(CAPAAction).filter(CAPAAction.id == capa_id).first()
    if not capa:
        return {"error": "CAPA not found"}

    capa.status = "completed"
    capa.completion_date = date.today()

    db.commit()

    return {"message": "CAPA completed"}


@router.put("/capa/{capa_id}/verify")
def verify_capa_effectiveness(
    capa_id: int,
    effectiveness_result: str,
    verified_by_id: int,
    db: Session = Depends(get_db)
):
    """Verify CAPA effectiveness"""

    capa = db.query(CAPAAction).filter(CAPAAction.id == capa_id).first()
    if not capa:
        return {"error": "CAPA not found"}

    capa.effectiveness_result = effectiveness_result
    capa.verified_by_id = verified_by_id
    capa.verification_date = date.today()
    capa.status = "verified"

    # If effective, close the NC
    if effectiveness_result == "effective":
        nc = db.query(NonConformance).filter(NonConformance.id == capa.nc_id).first()
        if nc:
            nc.status = "closed"
            nc.actual_closure_date = date.today()

    db.commit()

    return {"message": "CAPA effectiveness verified"}


@router.get("/{nc_id}/details")
def get_nc_details(nc_id: int, db: Session = Depends(get_db)):
    """Get NC with RCA and CAPA details"""

    nc = db.query(NonConformance).filter(NonConformance.id == nc_id).first()
    if not nc:
        return {"error": "NC not found"}

    rca = db.query(RootCauseAnalysis).filter(RootCauseAnalysis.nc_id == nc_id).first()
    capas = db.query(CAPAAction).filter(CAPAAction.nc_id == nc_id).all()

    return {
        "nonconformance": nc,
        "root_cause_analysis": rca,
        "capa_actions": capas
    }
