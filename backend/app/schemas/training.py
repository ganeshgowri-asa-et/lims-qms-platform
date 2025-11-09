"""
Training & Competency Pydantic Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal


# ============================================================================
# Training Master Schemas
# ============================================================================

class TrainingMasterBase(BaseModel):
    training_code: str = Field(..., max_length=50)
    training_name: str = Field(..., max_length=255)
    description: Optional[str] = None
    category: str = Field(..., max_length=100)
    type: str = Field(..., max_length=50)
    duration_hours: Optional[Decimal] = None
    validity_months: Optional[int] = None
    trainer: Optional[str] = Field(None, max_length=100)
    training_material_path: Optional[str] = None
    prerequisites: Optional[str] = None
    competency_level: Optional[str] = Field(None, max_length=50)
    applicable_roles: Optional[List[str]] = None
    status: str = Field(default="Active", max_length=50)


class TrainingMasterCreate(TrainingMasterBase):
    created_by: str = Field(..., max_length=100)


class TrainingMasterUpdate(BaseModel):
    training_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, max_length=50)
    duration_hours: Optional[Decimal] = None
    validity_months: Optional[int] = None
    trainer: Optional[str] = Field(None, max_length=100)
    training_material_path: Optional[str] = None
    prerequisites: Optional[str] = None
    competency_level: Optional[str] = Field(None, max_length=50)
    applicable_roles: Optional[List[str]] = None
    status: Optional[str] = Field(None, max_length=50)


class TrainingMasterResponse(TrainingMasterBase):
    id: int
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Employee Training Matrix Schemas
# ============================================================================

class EmployeeTrainingMatrixBase(BaseModel):
    employee_id: str = Field(..., max_length=50)
    employee_name: str = Field(..., max_length=200)
    department: str = Field(..., max_length=100)
    job_role: str = Field(..., max_length=100)
    training_id: int
    required: bool = True
    current_level: Optional[str] = Field(None, max_length=50)
    target_level: Optional[str] = Field(None, max_length=50)
    last_trained_date: Optional[date] = None
    certificate_valid_until: Optional[date] = None
    status: str = Field(default="Required", max_length=50)
    competency_score: Optional[Decimal] = None
    competency_status: Optional[str] = Field(None, max_length=50)
    gap_analysis: Optional[str] = None


class EmployeeTrainingMatrixCreate(EmployeeTrainingMatrixBase):
    pass


class EmployeeTrainingMatrixUpdate(BaseModel):
    required: Optional[bool] = None
    current_level: Optional[str] = Field(None, max_length=50)
    target_level: Optional[str] = Field(None, max_length=50)
    last_trained_date: Optional[date] = None
    certificate_valid_until: Optional[date] = None
    status: Optional[str] = Field(None, max_length=50)
    competency_score: Optional[Decimal] = None
    competency_status: Optional[str] = Field(None, max_length=50)
    gap_analysis: Optional[str] = None


class EmployeeTrainingMatrixResponse(EmployeeTrainingMatrixBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Training Attendance Schemas
# ============================================================================

class TrainingAttendanceBase(BaseModel):
    training_id: int
    training_date: date
    training_end_date: Optional[date] = None
    location: Optional[str] = Field(None, max_length=200)
    trainer_name: Optional[str] = Field(None, max_length=200)
    trainer_qualification: Optional[str] = Field(None, max_length=200)
    employee_id: str = Field(..., max_length=50)
    employee_name: str = Field(..., max_length=200)
    department: Optional[str] = Field(None, max_length=100)
    attendance_status: str = Field(default="Present", max_length=50)
    pre_test_score: Optional[Decimal] = None
    post_test_score: Optional[Decimal] = None
    practical_score: Optional[Decimal] = None
    overall_score: Optional[Decimal] = None
    pass_fail: str = Field(default="Pass", max_length=20)
    certificate_number: Optional[str] = Field(None, max_length=100)
    certificate_issue_date: Optional[date] = None
    certificate_valid_until: Optional[date] = None
    certificate_path: Optional[str] = None
    feedback_rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_comments: Optional[str] = None
    effectiveness_score: Optional[Decimal] = None
    qsf_form: Optional[str] = Field(None, max_length=20)
    form_path: Optional[str] = None


class TrainingAttendanceCreate(TrainingAttendanceBase):
    created_by: str = Field(..., max_length=100)


class TrainingAttendanceUpdate(BaseModel):
    training_end_date: Optional[date] = None
    location: Optional[str] = Field(None, max_length=200)
    trainer_name: Optional[str] = Field(None, max_length=200)
    trainer_qualification: Optional[str] = Field(None, max_length=200)
    attendance_status: Optional[str] = Field(None, max_length=50)
    pre_test_score: Optional[Decimal] = None
    post_test_score: Optional[Decimal] = None
    practical_score: Optional[Decimal] = None
    overall_score: Optional[Decimal] = None
    pass_fail: Optional[str] = Field(None, max_length=20)
    certificate_number: Optional[str] = Field(None, max_length=100)
    certificate_issue_date: Optional[date] = None
    certificate_valid_until: Optional[date] = None
    certificate_path: Optional[str] = None
    feedback_rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_comments: Optional[str] = None
    effectiveness_score: Optional[Decimal] = None
    qsf_form: Optional[str] = Field(None, max_length=20)
    form_path: Optional[str] = None


class TrainingAttendanceResponse(TrainingAttendanceBase):
    id: int
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Competency Assessment Schemas
# ============================================================================

class CompetencyAssessmentBase(BaseModel):
    employee_id: str = Field(..., max_length=50)
    employee_name: str = Field(..., max_length=200)
    assessment_date: date
    assessor: str = Field(..., max_length=100)
    job_role: str = Field(..., max_length=100)
    competencies: Optional[Dict[str, Any]] = None
    overall_competency_level: Optional[str] = Field(None, max_length=50)
    gaps_identified: Optional[str] = None
    development_plan: Optional[str] = None
    next_assessment_date: Optional[date] = None
    status: str = Field(default="Completed", max_length=50)


class CompetencyAssessmentCreate(CompetencyAssessmentBase):
    pass


class CompetencyAssessmentResponse(CompetencyAssessmentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Competency Gap Analysis Response
# ============================================================================

class CompetencyGap(BaseModel):
    employee_id: str
    employee_name: str
    department: str
    job_role: str
    training_name: str
    category: str
    current_level: Optional[str]
    target_level: Optional[str]
    status: str
    competency_status: Optional[str]
    last_trained_date: Optional[date]
    certificate_valid_until: Optional[date]
    gap_status: str
    days_until_expiry: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CompetencyGapSummary(BaseModel):
    total_employees: int
    total_training_requirements: int
    not_trained_count: int
    expired_count: int
    expiring_soon_count: int
    gap_exists_count: int
    competent_count: int
    gaps: List[CompetencyGap]


# ============================================================================
# Certificate Generation Schema
# ============================================================================

class CertificateRequest(BaseModel):
    attendance_id: int
    template: str = "default"  # Certificate template to use


class CertificateResponse(BaseModel):
    certificate_number: str
    certificate_path: str
    issue_date: date
    valid_until: date
