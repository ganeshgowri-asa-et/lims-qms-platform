"""
Test Request model for LIMS/QMS platform
"""
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import BaseModel


class TestRequest(Base, BaseModel):
    """Test Request table - QSF0601"""
    __tablename__ = "test_requests"

    # Auto-generated TRQ number (TRQ-YYYY-XXXXX)
    trq_number = Column(String(20), unique=True, nullable=False, index=True)

    # Customer Reference
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # Test Request Details
    project_name = Column(String(255), nullable=False)
    test_type = Column(String(100), nullable=False)
    priority = Column(String(20), nullable=False, default="medium")
    status = Column(String(50), nullable=False, default="draft")

    # Dates
    request_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    completion_date = Column(Date, nullable=True)

    # Description
    description = Column(Text, nullable=True)
    special_instructions = Column(Text, nullable=True)

    # Quote Information
    quote_required = Column(Boolean, default=False, nullable=False)
    quote_number = Column(String(20), nullable=True)
    quote_amount = Column(Numeric(10, 2), nullable=True)
    quote_approved = Column(Boolean, default=False, nullable=False)
    quote_approved_by = Column(String(255), nullable=True)
    quote_approved_date = Column(Date, nullable=True)

    # Requester Information
    requested_by = Column(String(255), nullable=False)
    department = Column(String(100), nullable=True)
    contact_number = Column(String(50), nullable=True)

    # Approval Workflow
    submitted_by = Column(String(255), nullable=True)
    submitted_date = Column(Date, nullable=True)
    approved_by = Column(String(255), nullable=True)
    approved_date = Column(Date, nullable=True)

    # Barcode
    barcode_data = Column(Text, nullable=True)  # Base64 encoded barcode image

    # Relationships
    customer = relationship("Customer", back_populates="test_requests")
    samples = relationship("Sample", back_populates="test_request", cascade="all, delete-orphan")
    test_parameters = relationship("TestParameter", back_populates="test_request", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestRequest {self.trq_number}: {self.project_name}>"
