"""
Training & Competency Management Models
"""
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Boolean,
    DECIMAL, ForeignKey, ARRAY, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class TrainingMaster(Base):
    """Training Master table - stores all training programs"""
    __tablename__ = "training_master"

    id = Column(Integer, primary_key=True, index=True)
    training_code = Column(String(50), unique=True, nullable=False, index=True)
    training_name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    duration_hours = Column(DECIMAL(5, 2))
    validity_months = Column(Integer)
    trainer = Column(String(100))
    training_material_path = Column(String(500))
    prerequisites = Column(Text)
    competency_level = Column(String(50))
    applicable_roles = Column(ARRAY(String))
    status = Column(String(50), default="Active", index=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    training_matrix = relationship("EmployeeTrainingMatrix", back_populates="training")
    attendance_records = relationship("TrainingAttendance", back_populates="training")


class EmployeeTrainingMatrix(Base):
    """Employee Training Matrix - tracks required training per employee"""
    __tablename__ = "employee_training_matrix"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False, index=True)
    employee_name = Column(String(200), nullable=False)
    department = Column(String(100), nullable=False)
    job_role = Column(String(100), nullable=False)
    training_id = Column(Integer, ForeignKey("training_master.id", ondelete="CASCADE"))
    required = Column(Boolean, default=True)
    current_level = Column(String(50))
    target_level = Column(String(50))
    last_trained_date = Column(Date)
    certificate_valid_until = Column(Date)
    status = Column(String(50), default="Required", index=True)
    competency_score = Column(DECIMAL(5, 2))
    competency_status = Column(String(50))
    gap_analysis = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    training = relationship("TrainingMaster", back_populates="training_matrix")


class TrainingAttendance(Base):
    """Training Attendance & Assessment Records"""
    __tablename__ = "training_attendance"

    id = Column(Integer, primary_key=True, index=True)
    training_id = Column(Integer, ForeignKey("training_master.id", ondelete="CASCADE"))
    training_date = Column(Date, nullable=False, index=True)
    training_end_date = Column(Date)
    location = Column(String(200))
    trainer_name = Column(String(200))
    trainer_qualification = Column(String(200))
    employee_id = Column(String(50), nullable=False, index=True)
    employee_name = Column(String(200), nullable=False)
    department = Column(String(100))
    attendance_status = Column(String(50), default="Present")
    pre_test_score = Column(DECIMAL(5, 2))
    post_test_score = Column(DECIMAL(5, 2))
    practical_score = Column(DECIMAL(5, 2))
    overall_score = Column(DECIMAL(5, 2))
    pass_fail = Column(String(20), default="Pass")
    certificate_number = Column(String(100))
    certificate_issue_date = Column(Date)
    certificate_valid_until = Column(Date)
    certificate_path = Column(String(500))
    feedback_rating = Column(Integer)
    feedback_comments = Column(Text)
    effectiveness_score = Column(DECIMAL(5, 2))
    qsf_form = Column(String(20))
    form_path = Column(String(500))
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    training = relationship("TrainingMaster", back_populates="attendance_records")
    effectiveness = relationship("TrainingEffectiveness", back_populates="attendance")


class TrainingEffectiveness(Base):
    """Training Effectiveness Evaluation"""
    __tablename__ = "training_effectiveness"

    id = Column(Integer, primary_key=True, index=True)
    attendance_id = Column(Integer, ForeignKey("training_attendance.id", ondelete="CASCADE"))
    evaluation_date = Column(Date, nullable=False)
    evaluator = Column(String(100), nullable=False)
    knowledge_retention = Column(DECIMAL(5, 2))
    practical_application = Column(DECIMAL(5, 2))
    behavior_change = Column(DECIMAL(5, 2))
    business_impact = Column(DECIMAL(5, 2))
    overall_effectiveness = Column(DECIMAL(5, 2))
    comments = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    attendance = relationship("TrainingAttendance", back_populates="effectiveness")


class CompetencyAssessment(Base):
    """Competency Assessment Records"""
    __tablename__ = "competency_assessment"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False, index=True)
    employee_name = Column(String(200), nullable=False)
    assessment_date = Column(Date, nullable=False)
    assessor = Column(String(100), nullable=False)
    job_role = Column(String(100), nullable=False)
    competencies = Column(JSON)  # JSON array of competency assessments
    overall_competency_level = Column(String(50))
    gaps_identified = Column(Text)
    development_plan = Column(Text)
    next_assessment_date = Column(Date)
    status = Column(String(50), default="Completed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
