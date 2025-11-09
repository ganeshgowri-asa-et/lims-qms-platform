"""
Training & Competency Models (Session 4)
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, Float, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.core.database import Base


class TrainingMaster(Base):
    """Training course master table"""
    __tablename__ = "training_master"

    id = Column(Integer, primary_key=True, index=True)
    training_code = Column(String(50), unique=True, nullable=False, index=True)
    training_name = Column(String(200), nullable=False)
    training_type = Column(String(50))  # technical, quality, safety, soft_skills
    duration_hours = Column(Float)
    trainer_name = Column(String(100))
    validity_period_months = Column(Integer)  # Re-training period
    competency_criteria = Column(Text)  # JSON array
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    training_matrix = relationship("EmployeeTrainingMatrix", back_populates="training")
    attendance_records = relationship("TrainingAttendance", back_populates="training")


class EmployeeTrainingMatrix(Base):
    """Employee training requirements matrix"""
    __tablename__ = "employee_training_matrix"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    training_id = Column(Integer, ForeignKey("training_master.id"), nullable=False)
    is_required = Column(Boolean, default=True)
    last_completed_date = Column(Date)
    next_due_date = Column(Date, index=True)
    competency_score = Column(Float)  # Out of 100
    competency_status = Column(String(50))  # competent, requires_improvement, not_competent
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    training = relationship("TrainingMaster", back_populates="training_matrix")


class TrainingAttendance(Base):
    """Training attendance and assessment records"""
    __tablename__ = "training_attendance"

    id = Column(Integer, primary_key=True, index=True)
    training_id = Column(Integer, ForeignKey("training_master.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    training_date = Column(Date, nullable=False)
    attendance_status = Column(String(50))  # present, absent, partial
    assessment_score = Column(Float)
    assessment_result = Column(String(50))  # pass, fail
    trainer_remarks = Column(Text)
    certificate_number = Column(String(100))
    certificate_path = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    training = relationship("TrainingMaster", back_populates="attendance_records")
