"""
FastAPI Endpoints for Audit & Risk Management System
"""
from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, func, desc, and_
from sqlalchemy.orm import Session, sessionmaker
from backend.database.models import (
    AuditProgram, AuditSchedule, AuditFinding,
    RiskRegister, RiskReviewHistory, ComplianceTracking
)
from backend.config import settings

# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter(prefix="/audit-risk", tags=["Audit & Risk Management"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================================================================
# PYDANTIC SCHEMAS
# ================================================================

class AuditProgramCreate(BaseModel):
    program_year: int = Field(..., ge=2024)
    program_title: str
    scope: Optional[str] = None
    objectives: Optional[str] = None
    prepared_by: Optional[str] = None
    reviewed_by: Optional[str] = None
    approved_by: Optional[str] = None
    status: str = "DRAFT"
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class AuditProgramResponse(AuditProgramCreate):
    id: int
    program_number: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuditScheduleCreate(BaseModel):
    program_id: Optional[int] = None
    audit_type: str
    audit_scope: str
    department: Optional[str] = None
    process_area: Optional[str] = None
    standard_reference: Optional[str] = None
    planned_date: date
    actual_date: Optional[date] = None
    duration_days: Optional[int] = None
    lead_auditor: Optional[str] = None
    audit_team: Optional[str] = None
    auditee: Optional[str] = None
    status: str = "SCHEDULED"
    remarks: Optional[str] = None


class AuditScheduleResponse(AuditScheduleCreate):
    id: int
    audit_number: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuditFindingCreate(BaseModel):
    audit_id: int
    finding_type: str
    severity: Optional[str] = None
    category: Optional[str] = None
    clause_reference: Optional[str] = None
    area_audited: Optional[str] = None
    description: str
    objective_evidence: Optional[str] = None
    requirement: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    responsible_person: Optional[str] = None
    target_date: Optional[date] = None
    actual_closure_date: Optional[date] = None
    status: str = "OPEN"
    nc_reference: Optional[str] = None
    effectiveness_verified: bool = False
    verified_by: Optional[str] = None
    verified_date: Optional[date] = None
    attachments: Optional[str] = None


class AuditFindingResponse(AuditFindingCreate):
    id: int
    finding_number: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RiskRegisterCreate(BaseModel):
    risk_category: str
    process_area: Optional[str] = None
    department: Optional[str] = None
    risk_description: str
    risk_source: Optional[str] = None
    consequences: Optional[str] = None
    existing_controls: Optional[str] = None
    inherent_likelihood: int = Field(..., ge=1, le=5)
    inherent_impact: int = Field(..., ge=1, le=5)
    residual_likelihood: int = Field(..., ge=1, le=5)
    residual_impact: int = Field(..., ge=1, le=5)
    risk_treatment: Optional[str] = None
    treatment_plan: Optional[str] = None
    risk_owner: Optional[str] = None
    target_date: Optional[date] = None
    review_frequency: Optional[str] = None
    last_review_date: Optional[date] = None
    next_review_date: Optional[date] = None
    status: str = "ACTIVE"
    remarks: Optional[str] = None


class RiskRegisterResponse(RiskRegisterCreate):
    id: int
    risk_number: str
    inherent_risk_score: int
    inherent_risk_level: str
    residual_risk_score: int
    residual_risk_level: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComplianceTrackingCreate(BaseModel):
    standard_name: str
    clause_number: str
    clause_title: Optional[str] = None
    requirement: Optional[str] = None
    compliance_status: str = "COMPLIANT"
    evidence_reference: Optional[str] = None
    last_audit_date: Optional[date] = None
    next_audit_date: Optional[date] = None
    responsible_person: Optional[str] = None
    remarks: Optional[str] = None


class ComplianceTrackingResponse(ComplianceTrackingCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ================================================================
# UTILITY FUNCTIONS
# ================================================================

def generate_audit_number(db: Session) -> str:
    """Generate next audit number: AUD-YYYY-XXX"""
    current_year = datetime.now().year
    prefix = f"AUD-{current_year}-"

    last_audit = db.query(AuditSchedule).filter(
        AuditSchedule.audit_number.like(f"{prefix}%")
    ).order_by(desc(AuditSchedule.audit_number)).first()

    if last_audit:
        last_seq = int(last_audit.audit_number.split("-")[-1])
        next_seq = last_seq + 1
    else:
        next_seq = 1

    return f"{prefix}{str(next_seq).zfill(3)}"


def generate_finding_number(db: Session) -> str:
    """Generate next finding number: FND-YYYY-XXX"""
    current_year = datetime.now().year
    prefix = f"FND-{current_year}-"

    last_finding = db.query(AuditFinding).filter(
        AuditFinding.finding_number.like(f"{prefix}%")
    ).order_by(desc(AuditFinding.finding_number)).first()

    if last_finding:
        last_seq = int(last_finding.finding_number.split("-")[-1])
        next_seq = last_seq + 1
    else:
        next_seq = 1

    return f"{prefix}{str(next_seq).zfill(3)}"


def generate_risk_number(db: Session) -> str:
    """Generate next risk number: RISK-YYYY-XXX"""
    current_year = datetime.now().year
    prefix = f"RISK-{current_year}-"

    last_risk = db.query(RiskRegister).filter(
        RiskRegister.risk_number.like(f"{prefix}%")
    ).order_by(desc(RiskRegister.risk_number)).first()

    if last_risk:
        last_seq = int(last_risk.risk_number.split("-")[-1])
        next_seq = last_seq + 1
    else:
        next_seq = 1

    return f"{prefix}{str(next_seq).zfill(3)}"


def generate_program_number(db: Session, year: int) -> str:
    """Generate program number: QSF1701-YYYY"""
    return f"QSF1701-{year}"


# ================================================================
# AUDIT PROGRAM ENDPOINTS
# ================================================================

@router.post("/programs", response_model=AuditProgramResponse)
def create_audit_program(program: AuditProgramCreate, db: Session = Depends(get_db)):
    """Create a new audit program"""
    program_number = generate_program_number(db, program.program_year)

    db_program = AuditProgram(
        program_number=program_number,
        **program.model_dump()
    )
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program


@router.get("/programs", response_model=List[AuditProgramResponse])
def get_audit_programs(
    year: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all audit programs with optional filters"""
    query = db.query(AuditProgram)

    if year:
        query = query.filter(AuditProgram.program_year == year)
    if status:
        query = query.filter(AuditProgram.status == status)

    return query.order_by(desc(AuditProgram.program_year)).all()


@router.get("/programs/{program_id}", response_model=AuditProgramResponse)
def get_audit_program(program_id: int, db: Session = Depends(get_db)):
    """Get a specific audit program"""
    program = db.query(AuditProgram).filter(AuditProgram.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Audit program not found")
    return program


@router.put("/programs/{program_id}", response_model=AuditProgramResponse)
def update_audit_program(
    program_id: int,
    program_update: AuditProgramCreate,
    db: Session = Depends(get_db)
):
    """Update an audit program"""
    db_program = db.query(AuditProgram).filter(AuditProgram.id == program_id).first()
    if not db_program:
        raise HTTPException(status_code=404, detail="Audit program not found")

    for key, value in program_update.model_dump(exclude_unset=True).items():
        setattr(db_program, key, value)

    db.commit()
    db.refresh(db_program)
    return db_program


@router.delete("/programs/{program_id}")
def delete_audit_program(program_id: int, db: Session = Depends(get_db)):
    """Delete an audit program"""
    db_program = db.query(AuditProgram).filter(AuditProgram.id == program_id).first()
    if not db_program:
        raise HTTPException(status_code=404, detail="Audit program not found")

    db.delete(db_program)
    db.commit()
    return {"message": "Audit program deleted successfully"}


# ================================================================
# AUDIT SCHEDULE ENDPOINTS
# ================================================================

@router.post("/schedules", response_model=AuditScheduleResponse)
def create_audit_schedule(schedule: AuditScheduleCreate, db: Session = Depends(get_db)):
    """Create a new audit schedule"""
    audit_number = generate_audit_number(db)

    db_schedule = AuditSchedule(
        audit_number=audit_number,
        **schedule.model_dump()
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.get("/schedules", response_model=List[AuditScheduleResponse])
def get_audit_schedules(
    program_id: Optional[int] = None,
    audit_type: Optional[str] = None,
    status: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all audit schedules with optional filters"""
    query = db.query(AuditSchedule)

    if program_id:
        query = query.filter(AuditSchedule.program_id == program_id)
    if audit_type:
        query = query.filter(AuditSchedule.audit_type == audit_type)
    if status:
        query = query.filter(AuditSchedule.status == status)
    if department:
        query = query.filter(AuditSchedule.department == department)

    return query.order_by(AuditSchedule.planned_date).all()


@router.get("/schedules/{schedule_id}", response_model=AuditScheduleResponse)
def get_audit_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """Get a specific audit schedule"""
    schedule = db.query(AuditSchedule).filter(AuditSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Audit schedule not found")
    return schedule


@router.put("/schedules/{schedule_id}", response_model=AuditScheduleResponse)
def update_audit_schedule(
    schedule_id: int,
    schedule_update: AuditScheduleCreate,
    db: Session = Depends(get_db)
):
    """Update an audit schedule"""
    db_schedule = db.query(AuditSchedule).filter(AuditSchedule.id == schedule_id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Audit schedule not found")

    for key, value in schedule_update.model_dump(exclude_unset=True).items():
        setattr(db_schedule, key, value)

    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.delete("/schedules/{schedule_id}")
def delete_audit_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """Delete an audit schedule"""
    db_schedule = db.query(AuditSchedule).filter(AuditSchedule.id == schedule_id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Audit schedule not found")

    db.delete(db_schedule)
    db.commit()
    return {"message": "Audit schedule deleted successfully"}


# ================================================================
# AUDIT FINDINGS ENDPOINTS
# ================================================================

@router.post("/findings", response_model=AuditFindingResponse)
def create_audit_finding(finding: AuditFindingCreate, db: Session = Depends(get_db)):
    """Create a new audit finding"""
    finding_number = generate_finding_number(db)

    db_finding = AuditFinding(
        finding_number=finding_number,
        **finding.model_dump()
    )
    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)
    return db_finding


@router.get("/findings", response_model=List[AuditFindingResponse])
def get_audit_findings(
    audit_id: Optional[int] = None,
    finding_type: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all audit findings with optional filters"""
    query = db.query(AuditFinding)

    if audit_id:
        query = query.filter(AuditFinding.audit_id == audit_id)
    if finding_type:
        query = query.filter(AuditFinding.finding_type == finding_type)
    if status:
        query = query.filter(AuditFinding.status == status)
    if severity:
        query = query.filter(AuditFinding.severity == severity)

    return query.order_by(desc(AuditFinding.created_at)).all()


@router.get("/findings/{finding_id}", response_model=AuditFindingResponse)
def get_audit_finding(finding_id: int, db: Session = Depends(get_db)):
    """Get a specific audit finding"""
    finding = db.query(AuditFinding).filter(AuditFinding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Audit finding not found")
    return finding


@router.put("/findings/{finding_id}", response_model=AuditFindingResponse)
def update_audit_finding(
    finding_id: int,
    finding_update: AuditFindingCreate,
    db: Session = Depends(get_db)
):
    """Update an audit finding"""
    db_finding = db.query(AuditFinding).filter(AuditFinding.id == finding_id).first()
    if not db_finding:
        raise HTTPException(status_code=404, detail="Audit finding not found")

    for key, value in finding_update.model_dump(exclude_unset=True).items():
        setattr(db_finding, key, value)

    db.commit()
    db.refresh(db_finding)
    return db_finding


@router.delete("/findings/{finding_id}")
def delete_audit_finding(finding_id: int, db: Session = Depends(get_db)):
    """Delete an audit finding"""
    db_finding = db.query(AuditFinding).filter(AuditFinding.id == finding_id).first()
    if not db_finding:
        raise HTTPException(status_code=404, detail="Audit finding not found")

    db.delete(db_finding)
    db.commit()
    return {"message": "Audit finding deleted successfully"}


# ================================================================
# RISK REGISTER ENDPOINTS
# ================================================================

@router.post("/risks", response_model=RiskRegisterResponse)
def create_risk(risk: RiskRegisterCreate, db: Session = Depends(get_db)):
    """Create a new risk"""
    risk_number = generate_risk_number(db)

    db_risk = RiskRegister(
        risk_number=risk_number,
        **risk.model_dump()
    )
    db.add(db_risk)
    db.commit()
    db.refresh(db_risk)
    return db_risk


@router.get("/risks", response_model=List[RiskRegisterResponse])
def get_risks(
    risk_category: Optional[str] = None,
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all risks with optional filters"""
    query = db.query(RiskRegister)

    if risk_category:
        query = query.filter(RiskRegister.risk_category == risk_category)
    if status:
        query = query.filter(RiskRegister.status == status)
    if department:
        query = query.filter(RiskRegister.department == department)

    risks = query.order_by(desc(RiskRegister.created_at)).all()

    # Filter by risk level if specified (computed property)
    if risk_level:
        risks = [r for r in risks if r.residual_risk_level == risk_level]

    return risks


@router.get("/risks/{risk_id}", response_model=RiskRegisterResponse)
def get_risk(risk_id: int, db: Session = Depends(get_db)):
    """Get a specific risk"""
    risk = db.query(RiskRegister).filter(RiskRegister.id == risk_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


@router.put("/risks/{risk_id}", response_model=RiskRegisterResponse)
def update_risk(
    risk_id: int,
    risk_update: RiskRegisterCreate,
    db: Session = Depends(get_db)
):
    """Update a risk"""
    db_risk = db.query(RiskRegister).filter(RiskRegister.id == risk_id).first()
    if not db_risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    for key, value in risk_update.model_dump(exclude_unset=True).items():
        setattr(db_risk, key, value)

    db.commit()
    db.refresh(db_risk)
    return db_risk


@router.delete("/risks/{risk_id}")
def delete_risk(risk_id: int, db: Session = Depends(get_db)):
    """Delete a risk"""
    db_risk = db.query(RiskRegister).filter(RiskRegister.id == risk_id).first()
    if not db_risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    db.delete(db_risk)
    db.commit()
    return {"message": "Risk deleted successfully"}


# ================================================================
# COMPLIANCE TRACKING ENDPOINTS
# ================================================================

@router.post("/compliance", response_model=ComplianceTrackingResponse)
def create_compliance_tracking(
    compliance: ComplianceTrackingCreate,
    db: Session = Depends(get_db)
):
    """Create a new compliance tracking record"""
    db_compliance = ComplianceTracking(**compliance.model_dump())
    db.add(db_compliance)
    db.commit()
    db.refresh(db_compliance)
    return db_compliance


@router.get("/compliance", response_model=List[ComplianceTrackingResponse])
def get_compliance_tracking(
    standard_name: Optional[str] = None,
    compliance_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all compliance tracking records with optional filters"""
    query = db.query(ComplianceTracking)

    if standard_name:
        query = query.filter(ComplianceTracking.standard_name == standard_name)
    if compliance_status:
        query = query.filter(ComplianceTracking.compliance_status == compliance_status)

    return query.order_by(ComplianceTracking.standard_name, ComplianceTracking.clause_number).all()


@router.get("/compliance/{compliance_id}", response_model=ComplianceTrackingResponse)
def get_compliance_record(compliance_id: int, db: Session = Depends(get_db)):
    """Get a specific compliance tracking record"""
    compliance = db.query(ComplianceTracking).filter(
        ComplianceTracking.id == compliance_id
    ).first()
    if not compliance:
        raise HTTPException(status_code=404, detail="Compliance record not found")
    return compliance


@router.put("/compliance/{compliance_id}", response_model=ComplianceTrackingResponse)
def update_compliance_tracking(
    compliance_id: int,
    compliance_update: ComplianceTrackingCreate,
    db: Session = Depends(get_db)
):
    """Update a compliance tracking record"""
    db_compliance = db.query(ComplianceTracking).filter(
        ComplianceTracking.id == compliance_id
    ).first()
    if not db_compliance:
        raise HTTPException(status_code=404, detail="Compliance record not found")

    for key, value in compliance_update.model_dump(exclude_unset=True).items():
        setattr(db_compliance, key, value)

    db.commit()
    db.refresh(db_compliance)
    return db_compliance


# ================================================================
# DASHBOARD & ANALYTICS ENDPOINTS
# ================================================================

@router.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary statistics"""
    # Audit statistics
    total_audits = db.query(AuditSchedule).count()
    scheduled_audits = db.query(AuditSchedule).filter(
        AuditSchedule.status == "SCHEDULED"
    ).count()
    completed_audits = db.query(AuditSchedule).filter(
        AuditSchedule.status == "COMPLETED"
    ).count()

    # Finding statistics
    total_findings = db.query(AuditFinding).count()
    open_findings = db.query(AuditFinding).filter(
        AuditFinding.status.in_(["OPEN", "IN_PROGRESS"])
    ).count()
    ncr_findings = db.query(AuditFinding).filter(
        AuditFinding.finding_type == "NCR"
    ).count()

    # Risk statistics
    total_risks = db.query(RiskRegister).filter(RiskRegister.status == "ACTIVE").count()
    risks = db.query(RiskRegister).filter(RiskRegister.status == "ACTIVE").all()

    high_critical_risks = sum(
        1 for r in risks if r.residual_risk_level in ["HIGH", "CRITICAL"]
    )

    # Compliance statistics
    total_clauses = db.query(ComplianceTracking).count()
    compliant_clauses = db.query(ComplianceTracking).filter(
        ComplianceTracking.compliance_status == "COMPLIANT"
    ).count()

    compliance_percentage = (
        round((compliant_clauses / total_clauses) * 100, 2) if total_clauses > 0 else 0
    )

    return {
        "audits": {
            "total": total_audits,
            "scheduled": scheduled_audits,
            "completed": completed_audits,
        },
        "findings": {
            "total": total_findings,
            "open": open_findings,
            "ncr": ncr_findings,
        },
        "risks": {
            "total": total_risks,
            "high_critical": high_critical_risks,
        },
        "compliance": {
            "total_clauses": total_clauses,
            "compliant": compliant_clauses,
            "compliance_percentage": compliance_percentage,
        },
    }


@router.get("/dashboard/risk-matrix")
def get_risk_matrix(db: Session = Depends(get_db)):
    """Get risk matrix data for 5x5 visualization"""
    risks = db.query(RiskRegister).filter(RiskRegister.status == "ACTIVE").all()

    matrix = {}
    for likelihood in range(1, 6):
        for impact in range(1, 6):
            key = f"{likelihood}x{impact}"
            matrix[key] = []

    for risk in risks:
        if risk.residual_likelihood and risk.residual_impact:
            key = f"{risk.residual_likelihood}x{risk.residual_impact}"
            matrix[key].append({
                "risk_number": risk.risk_number,
                "risk_description": risk.risk_description[:100],
                "risk_category": risk.risk_category,
            })

    return matrix


@router.get("/dashboard/upcoming-audits")
def get_upcoming_audits(days: int = 30, db: Session = Depends(get_db)):
    """Get upcoming audits within specified days"""
    from datetime import datetime, timedelta

    end_date = datetime.now().date() + timedelta(days=days)

    audits = db.query(AuditSchedule).filter(
        and_(
            AuditSchedule.status == "SCHEDULED",
            AuditSchedule.planned_date <= end_date
        )
    ).order_by(AuditSchedule.planned_date).all()

    return audits


@router.get("/dashboard/overdue-findings")
def get_overdue_findings(db: Session = Depends(get_db)):
    """Get overdue audit findings"""
    from datetime import datetime

    today = datetime.now().date()

    findings = db.query(AuditFinding).filter(
        and_(
            AuditFinding.status.in_(["OPEN", "IN_PROGRESS"]),
            AuditFinding.target_date < today
        )
    ).order_by(AuditFinding.target_date).all()

    return findings
