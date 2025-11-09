"""
Audit & Risk Management API (Session 8)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.audit_risk import AuditProgram, AuditSchedule, AuditFinding, RiskRegister


router = APIRouter()


class AuditProgramCreate(BaseModel):
    program_year: int
    program_objectives: str
    scope: str
    audit_criteria: str
    approved_by_id: int


class AuditScheduleCreate(BaseModel):
    audit_program_id: int
    audit_type: str
    audit_area: str
    planned_date: date
    lead_auditor_id: int


class AuditFindingCreate(BaseModel):
    audit_id: int
    finding_type: str
    clause_reference: str = None
    description: str
    evidence: str = None


class RiskCreate(BaseModel):
    risk_category: str
    risk_description: str
    process_area: str
    likelihood: int
    consequence: int
    mitigation_plan: str
    responsible_person_id: int


@router.post("/audit-program")
def create_audit_program(program: AuditProgramCreate, db: Session = Depends(get_db)):
    """Create annual audit program (QSF1701)"""

    db_program = AuditProgram(
        **program.dict(),
        approval_date=date.today()
    )

    db.add(db_program)
    db.commit()
    db.refresh(db_program)

    return {"message": "Audit program created", "id": db_program.id}


@router.get("/audit-program/{year}")
def get_audit_program(year: int, db: Session = Depends(get_db)):
    """Get audit program for a year"""
    program = db.query(AuditProgram).filter(AuditProgram.program_year == year).first()
    return program


@router.post("/audit-schedule")
def create_audit_schedule(schedule: AuditScheduleCreate, db: Session = Depends(get_db)):
    """Create audit schedule"""

    # Generate audit number
    year = schedule.planned_date.year
    last_audit = db.query(AuditSchedule).filter(
        AuditSchedule.audit_number.like(f"AUD-{year}-%")
    ).order_by(AuditSchedule.id.desc()).first()

    if last_audit:
        last_num = int(last_audit.audit_number.split("-")[-1])
        audit_number = f"AUD-{year}-{last_num + 1:03d}"
    else:
        audit_number = f"AUD-{year}-001"

    db_schedule = AuditSchedule(
        audit_number=audit_number,
        **schedule.dict(),
        status="planned"
    )

    db.add(db_schedule)
    db.commit()

    return {"message": "Audit scheduled", "audit_number": audit_number}


@router.get("/audit-schedule")
def list_audit_schedules(
    year: int = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List audit schedules"""
    query = db.query(AuditSchedule)

    if status:
        query = query.filter(AuditSchedule.status == status)

    schedules = query.offset(skip).limit(limit).all()
    return schedules


@router.post("/audit-findings")
def create_audit_finding(finding: AuditFindingCreate, db: Session = Depends(get_db)):
    """Create audit finding"""

    # Generate finding number
    audit = db.query(AuditSchedule).filter(AuditSchedule.id == finding.audit_id).first()
    if not audit:
        return {"error": "Audit not found"}

    audit_num = audit.audit_number
    last_finding = db.query(AuditFinding).filter(
        AuditFinding.finding_number.like(f"{audit_num}-%")
    ).order_by(AuditFinding.id.desc()).first()

    if last_finding:
        last_num = int(last_finding.finding_number.split("-")[-1])
        finding_number = f"{audit_num}-{last_num + 1:02d}"
    else:
        finding_number = f"{audit_num}-01"

    db_finding = AuditFinding(
        finding_number=finding_number,
        **finding.dict(),
        status="open"
    )

    db.add(db_finding)
    db.commit()

    return {"message": "Audit finding created", "finding_number": finding_number}


@router.get("/audit/{audit_id}/findings")
def get_audit_findings(audit_id: int, db: Session = Depends(get_db)):
    """Get findings for an audit"""
    findings = db.query(AuditFinding).filter(AuditFinding.audit_id == audit_id).all()
    return findings


@router.post("/risk-register")
def create_risk(risk: RiskCreate, db: Session = Depends(get_db)):
    """Create risk in risk register (5x5 matrix)"""

    # Generate risk ID
    last_risk = db.query(RiskRegister).order_by(RiskRegister.id.desc()).first()

    if last_risk and last_risk.risk_id:
        last_num = int(last_risk.risk_id.split("-")[-1])
        risk_id = f"RISK-{last_num + 1:03d}"
    else:
        risk_id = "RISK-001"

    # Calculate risk score and level
    risk_score = risk.likelihood * risk.consequence

    if risk_score <= 5:
        risk_level = "low"
    elif risk_score <= 12:
        risk_level = "medium"
    elif risk_score <= 19:
        risk_level = "high"
    else:
        risk_level = "critical"

    db_risk = RiskRegister(
        risk_id=risk_id,
        **risk.dict(),
        risk_score=risk_score,
        risk_level=risk_level,
        status="active"
    )

    db.add(db_risk)
    db.commit()

    return {
        "message": "Risk created",
        "risk_id": risk_id,
        "risk_score": risk_score,
        "risk_level": risk_level
    }


@router.get("/risk-register")
def list_risks(
    risk_level: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List risks with filters"""
    query = db.query(RiskRegister)

    if risk_level:
        query = query.filter(RiskRegister.risk_level == risk_level)

    if status:
        query = query.filter(RiskRegister.status == status)

    risks = query.offset(skip).limit(limit).all()
    return risks


@router.get("/risk-matrix")
def get_risk_matrix(db: Session = Depends(get_db)):
    """Get risk matrix visualization data (5x5)"""
    risks = db.query(RiskRegister).filter(RiskRegister.status == "active").all()

    # Group by likelihood and consequence
    matrix = {}
    for risk in risks:
        key = f"{risk.likelihood}-{risk.consequence}"
        if key not in matrix:
            matrix[key] = []
        matrix[key].append({
            "risk_id": risk.risk_id,
            "description": risk.risk_description,
            "risk_level": risk.risk_level
        })

    return matrix
