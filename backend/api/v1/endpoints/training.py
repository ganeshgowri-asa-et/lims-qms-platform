"""
Training & Competency API (Session 4)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.training import TrainingMaster, EmployeeTrainingMatrix, TrainingAttendance


router = APIRouter()


class TrainingCreate(BaseModel):
    training_code: str
    training_name: str
    training_type: str
    duration_hours: float = None
    validity_period_months: int = None


class TrainingResponse(BaseModel):
    id: int
    training_code: str
    training_name: str
    training_type: str

    class Config:
        from_attributes = True


class TrainingAttendanceCreate(BaseModel):
    training_id: int
    employee_id: int
    training_date: date
    attendance_status: str
    assessment_score: float = None
    assessment_result: str = None


@router.post("/", response_model=TrainingResponse)
def create_training(training: TrainingCreate, db: Session = Depends(get_db)):
    """Create new training course"""

    db_training = TrainingMaster(**training.dict())
    db.add(db_training)
    db.commit()
    db.refresh(db_training)

    return db_training


@router.get("/", response_model=List[TrainingResponse])
def list_trainings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all training courses"""
    trainings = db.query(TrainingMaster).offset(skip).limit(limit).all()
    return trainings


@router.post("/attendance")
def record_attendance(attendance: TrainingAttendanceCreate, db: Session = Depends(get_db)):
    """Record training attendance and assessment"""

    # Get training
    training = db.query(TrainingMaster).filter(TrainingMaster.id == attendance.training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")

    # Create attendance record
    db_attendance = TrainingAttendance(**attendance.dict())
    db.add(db_attendance)

    # Update employee training matrix
    matrix = db.query(EmployeeTrainingMatrix).filter(
        EmployeeTrainingMatrix.employee_id == attendance.employee_id,
        EmployeeTrainingMatrix.training_id == attendance.training_id
    ).first()

    if matrix:
        matrix.last_completed_date = attendance.training_date
        if training.validity_period_months:
            matrix.next_due_date = attendance.training_date + timedelta(days=training.validity_period_months * 30)
        matrix.competency_score = attendance.assessment_score
        if attendance.assessment_result == "pass":
            matrix.competency_status = "competent"
        else:
            matrix.competency_status = "requires_improvement"
    else:
        # Create new matrix entry
        next_due = None
        if training.validity_period_months:
            next_due = attendance.training_date + timedelta(days=training.validity_period_months * 30)

        matrix = EmployeeTrainingMatrix(
            employee_id=attendance.employee_id,
            training_id=attendance.training_id,
            last_completed_date=attendance.training_date,
            next_due_date=next_due,
            competency_score=attendance.assessment_score,
            competency_status="competent" if attendance.assessment_result == "pass" else "requires_improvement"
        )
        db.add(matrix)

    db.commit()

    return {"message": "Attendance recorded", "competency_status": matrix.competency_status}


@router.get("/employee/{employee_id}/matrix")
def get_employee_training_matrix(employee_id: int, db: Session = Depends(get_db)):
    """Get training matrix for employee"""
    matrix = db.query(EmployeeTrainingMatrix).filter(
        EmployeeTrainingMatrix.employee_id == employee_id
    ).all()

    return matrix


@router.get("/gaps")
def get_competency_gaps(db: Session = Depends(get_db)):
    """Get competency gaps across organization"""
    gaps = db.query(EmployeeTrainingMatrix).filter(
        EmployeeTrainingMatrix.competency_status.in_(["requires_improvement", "not_competent"])
    ).all()

    return gaps
