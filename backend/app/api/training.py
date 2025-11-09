"""
Training Management API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import date, timedelta
from decimal import Decimal

from ..database import get_db
from ..models.training import (
    TrainingMaster,
    EmployeeTrainingMatrix,
    TrainingAttendance,
    CompetencyAssessment
)
from ..schemas.training import (
    TrainingMasterCreate,
    TrainingMasterUpdate,
    TrainingMasterResponse,
    EmployeeTrainingMatrixCreate,
    EmployeeTrainingMatrixUpdate,
    EmployeeTrainingMatrixResponse,
    TrainingAttendanceCreate,
    TrainingAttendanceUpdate,
    TrainingAttendanceResponse,
    CompetencyAssessmentCreate,
    CompetencyAssessmentResponse,
    CompetencyGap,
    CompetencyGapSummary,
    CertificateRequest,
    CertificateResponse
)

router = APIRouter(prefix="/api/training", tags=["Training Management"])


# ============================================================================
# Training Master Endpoints
# ============================================================================

@router.post("/trainings", response_model=TrainingMasterResponse, status_code=status.HTTP_201_CREATED)
def create_training(training: TrainingMasterCreate, db: Session = Depends(get_db)):
    """Create a new training program"""
    # Check if training code already exists
    existing = db.query(TrainingMaster).filter(
        TrainingMaster.training_code == training.training_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Training code {training.training_code} already exists"
        )

    db_training = TrainingMaster(**training.model_dump())
    db.add(db_training)
    db.commit()
    db.refresh(db_training)
    return db_training


@router.get("/trainings", response_model=List[TrainingMasterResponse])
def get_trainings(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    status: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all training programs with optional filters"""
    query = db.query(TrainingMaster)

    if category:
        query = query.filter(TrainingMaster.category == category)
    if status:
        query = query.filter(TrainingMaster.status == status)
    if type:
        query = query.filter(TrainingMaster.type == type)

    trainings = query.offset(skip).limit(limit).all()
    return trainings


@router.get("/trainings/{training_id}", response_model=TrainingMasterResponse)
def get_training(training_id: int, db: Session = Depends(get_db)):
    """Get a specific training program"""
    training = db.query(TrainingMaster).filter(TrainingMaster.id == training_id).first()
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training {training_id} not found"
        )
    return training


@router.put("/trainings/{training_id}", response_model=TrainingMasterResponse)
def update_training(
    training_id: int,
    training_update: TrainingMasterUpdate,
    db: Session = Depends(get_db)
):
    """Update a training program"""
    training = db.query(TrainingMaster).filter(TrainingMaster.id == training_id).first()
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training {training_id} not found"
        )

    for field, value in training_update.model_dump(exclude_unset=True).items():
        setattr(training, field, value)

    db.commit()
    db.refresh(training)
    return training


@router.delete("/trainings/{training_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training(training_id: int, db: Session = Depends(get_db)):
    """Delete a training program"""
    training = db.query(TrainingMaster).filter(TrainingMaster.id == training_id).first()
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training {training_id} not found"
        )

    db.delete(training)
    db.commit()
    return None


# ============================================================================
# Employee Training Matrix Endpoints
# ============================================================================

@router.post("/matrix", response_model=EmployeeTrainingMatrixResponse, status_code=status.HTTP_201_CREATED)
def create_training_matrix(matrix: EmployeeTrainingMatrixCreate, db: Session = Depends(get_db)):
    """Create a new training matrix entry for an employee"""
    # Check if entry already exists
    existing = db.query(EmployeeTrainingMatrix).filter(
        and_(
            EmployeeTrainingMatrix.employee_id == matrix.employee_id,
            EmployeeTrainingMatrix.training_id == matrix.training_id
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Training matrix entry already exists for this employee and training"
        )

    db_matrix = EmployeeTrainingMatrix(**matrix.model_dump())
    db.add(db_matrix)
    db.commit()
    db.refresh(db_matrix)
    return db_matrix


@router.get("/matrix", response_model=List[EmployeeTrainingMatrixResponse])
def get_training_matrix(
    skip: int = 0,
    limit: int = 100,
    employee_id: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get training matrix entries with optional filters"""
    query = db.query(EmployeeTrainingMatrix)

    if employee_id:
        query = query.filter(EmployeeTrainingMatrix.employee_id == employee_id)
    if department:
        query = query.filter(EmployeeTrainingMatrix.department == department)
    if status:
        query = query.filter(EmployeeTrainingMatrix.status == status)

    matrix = query.offset(skip).limit(limit).all()
    return matrix


@router.put("/matrix/{matrix_id}", response_model=EmployeeTrainingMatrixResponse)
def update_training_matrix(
    matrix_id: int,
    matrix_update: EmployeeTrainingMatrixUpdate,
    db: Session = Depends(get_db)
):
    """Update a training matrix entry"""
    matrix = db.query(EmployeeTrainingMatrix).filter(
        EmployeeTrainingMatrix.id == matrix_id
    ).first()
    if not matrix:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training matrix entry {matrix_id} not found"
        )

    for field, value in matrix_update.model_dump(exclude_unset=True).items():
        setattr(matrix, field, value)

    db.commit()
    db.refresh(matrix)
    return matrix


# ============================================================================
# Training Attendance Endpoints
# ============================================================================

@router.post("/attendance", response_model=TrainingAttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(attendance: TrainingAttendanceCreate, db: Session = Depends(get_db)):
    """Record training attendance"""
    db_attendance = TrainingAttendance(**attendance.model_dump())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)

    # Update employee training matrix
    matrix_entry = db.query(EmployeeTrainingMatrix).filter(
        and_(
            EmployeeTrainingMatrix.employee_id == attendance.employee_id,
            EmployeeTrainingMatrix.training_id == attendance.training_id
        )
    ).first()

    if matrix_entry:
        matrix_entry.last_trained_date = attendance.training_date
        matrix_entry.certificate_valid_until = attendance.certificate_valid_until
        matrix_entry.status = "Completed" if attendance.pass_fail == "Pass" else "Failed"
        matrix_entry.competency_score = attendance.overall_score
        db.commit()

    return db_attendance


@router.get("/attendance", response_model=List[TrainingAttendanceResponse])
def get_attendance(
    skip: int = 0,
    limit: int = 100,
    training_id: Optional[int] = None,
    employee_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get training attendance records with optional filters"""
    query = db.query(TrainingAttendance)

    if training_id:
        query = query.filter(TrainingAttendance.training_id == training_id)
    if employee_id:
        query = query.filter(TrainingAttendance.employee_id == employee_id)
    if start_date:
        query = query.filter(TrainingAttendance.training_date >= start_date)
    if end_date:
        query = query.filter(TrainingAttendance.training_date <= end_date)

    attendance = query.order_by(TrainingAttendance.training_date.desc()).offset(skip).limit(limit).all()
    return attendance


@router.get("/attendance/{attendance_id}", response_model=TrainingAttendanceResponse)
def get_attendance_record(attendance_id: int, db: Session = Depends(get_db)):
    """Get a specific attendance record"""
    attendance = db.query(TrainingAttendance).filter(
        TrainingAttendance.id == attendance_id
    ).first()
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record {attendance_id} not found"
        )
    return attendance


@router.put("/attendance/{attendance_id}", response_model=TrainingAttendanceResponse)
def update_attendance(
    attendance_id: int,
    attendance_update: TrainingAttendanceUpdate,
    db: Session = Depends(get_db)
):
    """Update training attendance record"""
    attendance = db.query(TrainingAttendance).filter(
        TrainingAttendance.id == attendance_id
    ).first()
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record {attendance_id} not found"
        )

    for field, value in attendance_update.model_dump(exclude_unset=True).items():
        setattr(attendance, field, value)

    db.commit()
    db.refresh(attendance)
    return attendance


# ============================================================================
# Competency Assessment Endpoints
# ============================================================================

@router.post("/competency-assessment", response_model=CompetencyAssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_competency_assessment(
    assessment: CompetencyAssessmentCreate,
    db: Session = Depends(get_db)
):
    """Create a competency assessment"""
    db_assessment = CompetencyAssessment(**assessment.model_dump())
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment


@router.get("/competency-assessment", response_model=List[CompetencyAssessmentResponse])
def get_competency_assessments(
    skip: int = 0,
    limit: int = 100,
    employee_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get competency assessments"""
    query = db.query(CompetencyAssessment)

    if employee_id:
        query = query.filter(CompetencyAssessment.employee_id == employee_id)

    assessments = query.order_by(
        CompetencyAssessment.assessment_date.desc()
    ).offset(skip).limit(limit).all()
    return assessments


# ============================================================================
# Competency Gap Analysis Endpoints
# ============================================================================

@router.get("/competency-gaps", response_model=CompetencyGapSummary)
def get_competency_gaps(
    department: Optional[str] = None,
    employee_id: Optional[str] = None,
    gap_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive competency gap analysis

    Gap Status Options: Expired, Expiring Soon, Not Trained, Gap Exists, Competent
    """
    from ..services.competency_service import CompetencyService

    service = CompetencyService()
    return service.analyze_competency_gaps(
        db=db,
        department=department,
        employee_id=employee_id,
        gap_status_filter=gap_status
    )


@router.get("/employee/{employee_id}/development-plan")
def get_employee_development_plan(employee_id: str, db: Session = Depends(get_db)):
    """Get individual development plan for an employee"""
    from ..services.competency_service import CompetencyService

    service = CompetencyService()
    return service.get_employee_development_plan(db, employee_id)


@router.get("/department/{department}/competency-overview")
def get_department_competency_overview(department: str, db: Session = Depends(get_db)):
    """Get competency overview for a department"""
    from ..services.competency_service import CompetencyService

    service = CompetencyService()
    return service.get_department_competency_overview(db, department)


# ============================================================================
# Certificate Generation Endpoints
# ============================================================================

@router.post("/certificates/generate", response_model=CertificateResponse)
def generate_certificate(
    request: CertificateRequest,
    db: Session = Depends(get_db)
):
    """Generate training certificate for an attendance record"""
    from ..services.certificate_service import CertificateService

    service = CertificateService()
    try:
        result = service.generate_certificate(
            db=db,
            attendance_id=request.attendance_id,
            template=request.template
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/certificates/batch-generate")
def generate_batch_certificates(
    attendance_ids: List[int],
    template: str = "default",
    db: Session = Depends(get_db)
):
    """Generate certificates for multiple attendance records"""
    from ..services.certificate_service import CertificateService

    service = CertificateService()
    results = service.generate_batch_certificates(db, attendance_ids, template)
    return {"results": results}


# ============================================================================
# QSF Forms Generation Endpoints
# ============================================================================

@router.post("/qsf/attendance-record")
def generate_qsf0203(
    training_id: int,
    training_date: date,
    attendees: List[dict],
    db: Session = Depends(get_db)
):
    """Generate QSF0203 - Training Attendance Record"""
    from ..services.qsf_forms_service import QSFFormsService

    service = QSFFormsService()
    try:
        filepath = service.generate_qsf0203_training_attendance(
            db=db,
            training_id=training_id,
            training_date=training_date,
            attendees=attendees
        )
        return {"form": "QSF0203", "filepath": filepath}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/qsf/effectiveness-evaluation")
def generate_qsf0205(
    attendance_id: int,
    evaluation_data: dict,
    db: Session = Depends(get_db)
):
    """Generate QSF0205 - Training Effectiveness Evaluation"""
    from ..services.qsf_forms_service import QSFFormsService

    service = QSFFormsService()
    try:
        filepath = service.generate_qsf0205_training_effectiveness(
            db=db,
            attendance_id=attendance_id,
            evaluation_data=evaluation_data
        )
        return {"form": "QSF0205", "filepath": filepath}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/qsf/needs-assessment")
def generate_qsf0206(
    department: str,
    assessment_data: dict,
    db: Session = Depends(get_db)
):
    """Generate QSF0206 - Training Needs Assessment"""
    from ..services.qsf_forms_service import QSFFormsService

    service = QSFFormsService()
    filepath = service.generate_qsf0206_training_needs_assessment(
        db=db,
        department=department,
        assessment_data=assessment_data
    )
    return {"form": "QSF0206", "filepath": filepath}
