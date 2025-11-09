"""
HR and People Management models
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Enum, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class EmploymentStatusEnum(str, enum.Enum):
    """Employment status"""
    ACTIVE = "Active"
    ON_LEAVE = "On Leave"
    RESIGNED = "Resigned"
    TERMINATED = "Terminated"


class CandidateStatusEnum(str, enum.Enum):
    """Candidate hiring status"""
    APPLIED = "Applied"
    SCREENING = "Screening"
    INTERVIEW_SCHEDULED = "Interview Scheduled"
    INTERVIEWED = "Interviewed"
    OFFER_MADE = "Offer Made"
    OFFER_ACCEPTED = "Offer Accepted"
    OFFER_REJECTED = "Offer Rejected"
    HIRED = "Hired"
    REJECTED = "Rejected"


class LeaveTypeEnum(str, enum.Enum):
    """Leave types"""
    CASUAL = "Casual Leave"
    SICK = "Sick Leave"
    EARNED = "Earned Leave"
    MATERNITY = "Maternity Leave"
    PATERNITY = "Paternity Leave"
    UNPAID = "Unpaid Leave"


class Employee(BaseModel):
    """Employee model (extends User)"""
    __tablename__ = 'employees'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    employee_code = Column(String(50), unique=True, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    date_of_joining = Column(Date, nullable=False)
    date_of_exit = Column(Date, nullable=True)
    employment_status = Column(Enum(EmploymentStatusEnum), default=EmploymentStatusEnum.ACTIVE)
    employment_type = Column(String(50), nullable=True)  # Full-time, Part-time, Contract
    reporting_manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    salary = Column(Integer, nullable=True)
    bank_account = Column(String(100), nullable=True)
    emergency_contact = Column(JSON, nullable=True)
    qualifications = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    certifications = Column(JSON, nullable=True)
    documents = Column(JSON, nullable=True)  # Resume, certificates, etc.


class JobPosting(BaseModel):
    """Job posting model"""
    __tablename__ = 'job_postings'

    job_title = Column(String(200), nullable=False)
    job_code = Column(String(50), unique=True, nullable=False)
    department = Column(String(100), nullable=False)
    location = Column(String(200), nullable=True)
    employment_type = Column(String(50), nullable=True)
    experience_required = Column(String(100), nullable=True)
    salary_range = Column(String(100), nullable=True)
    job_description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    posted_date = Column(Date, nullable=True)
    closing_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    hiring_manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Relationships
    candidates = relationship('Candidate', back_populates='job_posting')


class Candidate(BaseModel):
    """Candidate model"""
    __tablename__ = 'candidates'

    job_posting_id = Column(Integer, ForeignKey('job_postings.id'), nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    resume_path = Column(String(500), nullable=True)
    cover_letter = Column(Text, nullable=True)
    status = Column(Enum(CandidateStatusEnum), default=CandidateStatusEnum.APPLIED)
    applied_date = Column(Date, nullable=True)
    interview_date = Column(Date, nullable=True)
    interview_notes = Column(Text, nullable=True)
    offer_date = Column(Date, nullable=True)
    offer_details = Column(JSON, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Relationships
    job_posting = relationship('JobPosting', back_populates='candidates')


class Training(BaseModel):
    """Training model"""
    __tablename__ = 'trainings'

    training_code = Column(String(50), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    training_type = Column(String(100), nullable=True)  # Technical, Soft Skills, Compliance
    trainer_name = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    duration_hours = Column(Integer, nullable=True)
    location = Column(String(200), nullable=True)
    max_participants = Column(Integer, nullable=True)
    cost = Column(Integer, nullable=True)
    participants = Column(JSON, nullable=True)  # List of employee IDs
    completion_status = Column(JSON, nullable=True)  # {employee_id: "completed"/"pending"}
    certificates_issued = Column(JSON, nullable=True)


class Leave(BaseModel):
    """Leave application model"""
    __tablename__ = 'leaves'

    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    leave_type = Column(Enum(LeaveTypeEnum), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    num_days = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String(50), default='pending')  # pending, approved, rejected, cancelled
    approver_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    approver_comments = Column(Text, nullable=True)
    approved_at = Column(String(255), nullable=True)


class Attendance(BaseModel):
    """Attendance tracking"""
    __tablename__ = 'attendance'

    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    date = Column(Date, nullable=False)
    check_in_time = Column(String(10), nullable=True)
    check_out_time = Column(String(10), nullable=True)
    status = Column(String(50), nullable=True)  # present, absent, half_day, on_leave
    hours_worked = Column(Float, nullable=True)
    location = Column(String(200), nullable=True)
    remarks = Column(Text, nullable=True)


class Performance(BaseModel):
    """Performance review model"""
    __tablename__ = 'performance_reviews'

    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    review_period = Column(String(50), nullable=False)  # Q1-2024, Annual-2024
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    review_date = Column(Date, nullable=True)
    goals = Column(JSON, nullable=True)
    achievements = Column(Text, nullable=True)
    areas_of_improvement = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 scale
    competencies = Column(JSON, nullable=True)  # {competency: rating}
    comments = Column(Text, nullable=True)
    status = Column(String(50), default='draft')  # draft, submitted, reviewed, completed
