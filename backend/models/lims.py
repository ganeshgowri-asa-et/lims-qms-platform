"""
LIMS Core - Test Request & Sample Management Models (Session 5)
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from backend.core.database import Base


class TestRequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SampleStatus(str, enum.Enum):
    RECEIVED = "received"
    IN_TESTING = "in_testing"
    TESTED = "tested"
    DISPOSED = "disposed"


class Customer(Base):
    """Customer master table"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(50), unique=True, nullable=False, index=True)
    company_name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    gstin = Column(String(50))
    is_active = Column(String(20), default="Yes")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    test_requests = relationship("TestRequest", back_populates="customer")


class TestRequest(Base):
    """Test request table"""
    __tablename__ = "test_requests"

    id = Column(Integer, primary_key=True, index=True)
    trq_number = Column(String(50), unique=True, nullable=False, index=True)  # TRQ-YYYY-XXX
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    request_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date)
    test_standard = Column(String(100))  # IEC 61215, IEC 61730, etc.
    sample_type = Column(String(100))  # Solar Module, Cell, etc.
    quantity = Column(Integer)
    status = Column(SQLEnum(TestRequestStatus), default=TestRequestStatus.PENDING)
    quotation_amount = Column(Float)
    po_number = Column(String(100))
    po_date = Column(Date)
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    remarks = Column(Text)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="test_requests")
    samples = relationship("Sample", back_populates="test_request")


class Sample(Base):
    """Sample tracking table"""
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(String(50), unique=True, nullable=False, index=True)
    test_request_id = Column(Integer, ForeignKey("test_requests.id"), nullable=False)
    sample_description = Column(String(200))
    manufacturer = Column(String(100))
    model_number = Column(String(100))
    serial_number = Column(String(100))
    received_date = Column(Date, nullable=False)
    status = Column(SQLEnum(SampleStatus), default=SampleStatus.RECEIVED)
    storage_location = Column(String(100))
    barcode_path = Column(String(500))
    condition_on_receipt = Column(Text)
    disposal_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    test_request = relationship("TestRequest", back_populates="samples")
    test_results = relationship("TestResult", back_populates="sample")


class TestParameter(Base):
    """Test parameters master"""
    __tablename__ = "test_parameters"

    id = Column(Integer, primary_key=True, index=True)
    parameter_code = Column(String(50), unique=True, nullable=False)
    parameter_name = Column(String(200), nullable=False)
    test_standard = Column(String(100))
    unit = Column(String(50))
    acceptance_criteria = Column(Text)
    test_method = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TestResult(Base):
    """Test results table"""
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)
    parameter_id = Column(Integer, ForeignKey("test_parameters.id"), nullable=False)
    test_date = Column(Date, nullable=False)
    measured_value = Column(Float)
    result = Column(String(50))  # Pass/Fail
    tested_by_id = Column(Integer, ForeignKey("users.id"))
    verified_by_id = Column(Integer, ForeignKey("users.id"))
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sample = relationship("Sample", back_populates="test_results")
